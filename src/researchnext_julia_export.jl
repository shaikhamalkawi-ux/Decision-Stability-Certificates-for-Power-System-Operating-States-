# Prospective official export only. No optimizer attachment or optimize! call.
using Pkg, SHA, Dates
using UnitCommitment, JuMP, MathOptInterface
const MOI = MathOptInterface
# JSON is an installed dependency of the pinned native package, not a new direct
# dependency of the isolated project. Use its already declared module binding.
const JSON = UnitCommitment.JSON

const CASE_SHA = "6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe"
const UC_COMMIT = "4f04f0dd6641b071fd7556346c3d7190c2ffdfe5"
const EXPECTED_VERSIONS = Dict("UnitCommitment"=>v"0.4.0", "JuMP"=>v"1.15.1",
    "MathOptInterface"=>v"1.20.1", "PackageCompiler"=>v"1.7.7")

digest(path) = bytes2hex(sha256(read(path)))
nowutc() = string(Dates.now(Dates.UTC)) * "Z"
ensure(condition, message) = condition || error(message)

function write_new(path, value)
    ensure(!ispath(path), "Output exists: " * path)
    open(path, "w") do io
        JSON.print(io, value, 2)
        write(io, '\n')
    end
end

function exact_value(x)
    if x isa Float64
        return Dict("type"=>"Float64", "bits_hex"=>string(reinterpret(UInt64, x), base=16, pad=16),
                    "display"=>repr(x))
    elseif x isa Bool || x isa Integer || x isa AbstractString || x === nothing
        return x
    elseif x isa AbstractVector || x isa Tuple
        return [exact_value(v) for v in x]
    end
    error("Unexpected native data type: " * string(typeof(x)))
end

function raw_function(f)
    if f isa MOI.VariableIndex
        return Dict("type"=>string(typeof(f)), "variable"=>f.value)
    elseif f isa MOI.ScalarAffineFunction{Float64}
        return Dict("type"=>string(typeof(f)), "constant"=>exact_value(f.constant),
            "terms"=>[Dict("variable"=>t.variable.value, "coefficient"=>exact_value(t.coefficient)) for t in f.terms])
    end
    error("Unsupported native constraint/objective function: " * string(typeof(f)))
end

function raw_set(s)
    if s isa MOI.ZeroOne
        return Dict("type"=>string(typeof(s)))
    elseif s isa MOI.EqualTo{Float64}
        return Dict("type"=>string(typeof(s)), "value"=>exact_value(s.value))
    elseif s isa MOI.LessThan{Float64}
        return Dict("type"=>string(typeof(s)), "upper"=>exact_value(s.upper))
    elseif s isa MOI.GreaterThan{Float64}
        return Dict("type"=>string(typeof(s)), "lower"=>exact_value(s.lower))
    elseif s isa MOI.Interval{Float64}
        return Dict("type"=>string(typeof(s)), "lower"=>exact_value(s.lower), "upper"=>exact_value(s.upper))
    end
    error("Unsupported native constraint set: " * string(typeof(s)))
end

function parsed_instance(instance)
    ensure(instance.time == 24 && length(instance.scenarios) == 1, "Wrong fixed horizon/scenario")
    sc = only(instance.scenarios)
    ensure(length(sc.thermal_units) == 10 && length(sc.buses) == 1 && isempty(sc.lines), "Wrong selected roster")
    ensure(isempty(sc.price_sensitive_loads) && isempty(sc.profiled_units) && isempty(sc.storage_units), "Unsupported native asset")
    units = Any[]
    for g in sc.thermal_units
        row = Dict{String,Any}("name"=>g.name, "bus"=>g.bus.name)
        for field in (:max_power, :min_power, :must_run, :min_power_cost, :min_uptime, :min_downtime,
                      :ramp_up_limit, :ramp_down_limit, :startup_limit, :shutdown_limit,
                      :initial_status, :initial_power, :commitment_status)
            row[string(field)] = exact_value(getproperty(g, field))
        end
        row["cost_segments"] = [Dict("mw"=>exact_value(s.mw), "cost"=>exact_value(s.cost)) for s in g.cost_segments]
        row["startup_categories"] = [Dict("delay"=>exact_value(s.delay), "cost"=>exact_value(s.cost)) for s in g.startup_categories]
        row["reserve_names"] = [r.name for r in g.reserves]
        push!(units, row)
    end
    return Dict("time"=>instance.time, "scenario_time"=>sc.time, "time_step_minutes"=>sc.time_step,
        "scenario_name"=>sc.name, "probability"=>exact_value(sc.probability),
        "power_balance_penalty"=>exact_value(sc.power_balance_penalty), "thermal_units"=>units,
        "buses"=>[Dict("name"=>b.name, "load"=>exact_value(b.load)) for b in sc.buses],
        "reserves"=>[Dict("name"=>r.name, "type"=>r.type, "amount"=>exact_value(r.amount),
            "shortfall_penalty"=>exact_value(r.shortfall_penalty)) for r in sc.reserves],
        "native_default_read_and_repair"=>true)
end

function export_backend(model)
    backend = JuMP.backend(model)
    ensure(MOI.Utilities.state(backend) == MOI.Utilities.NO_OPTIMIZER, "Optimizer attached unexpectedly")
    vars = MOI.get(backend, MOI.ListOfVariableIndices())
    variable_rows = [Dict("index"=>v.value, "name"=>MOI.get(backend, MOI.VariableName(), v)) for v in vars]
    aliases = Any[]
    for (family, container) in JuMP.object_dictionary(model)
        container isa AbstractDict || continue
        for (key, item) in container
            item isa JuMP.VariableRef || continue
            push!(aliases, Dict("family"=>string(family), "key"=>exact_value(key),
                                "variable"=>JuMP.index(item).value))
        end
    end
    constraints = Any[]
    typed_counts = Any[]
    binary_indices = Int[]
    affine_rows = 0
    # Enumerate the backend, not native dictionaries: duplicate PWL rows survive here.
    for (F, S) in MOI.get(backend, MOI.ListOfConstraintTypesPresent())
        indices = MOI.get(backend, MOI.ListOfConstraintIndices{F,S}())
        ensure(length(indices) == MOI.get(backend, MOI.NumberOfConstraints{F,S}()), "Typed row count mismatch")
        push!(typed_counts, Dict("function_type"=>string(F), "set_type"=>string(S), "count"=>length(indices)))
        for ci in indices
            f = MOI.get(backend, MOI.ConstraintFunction(), ci)
            s = MOI.get(backend, MOI.ConstraintSet(), ci)
            label = f isa MOI.VariableIndex ? "" : MOI.get(backend, MOI.ConstraintName(), ci)
            push!(constraints, Dict("index"=>ci.value, "function_type"=>string(F), "set_type"=>string(S),
                                   "name"=>label, "function"=>raw_function(f), "set"=>raw_set(s)))
            f isa MOI.ScalarAffineFunction{Float64} && (affine_rows += 1)
            f isa MOI.VariableIndex && s isa MOI.ZeroOne && push!(binary_indices, f.value)
        end
    end
    ensure(length(vars) == MOI.get(backend, MOI.NumberOfVariables()), "Variable inventory mismatch")
    alias_indices = [a["variable"] for a in aliases]
    ensure(sort(alias_indices) == sort([v.value for v in vars]), "Semantic aliases are not a one-to-one variable inventory")
    objective_type = MOI.get(backend, MOI.ObjectiveFunctionType())
    objective = MOI.get(backend, MOI.ObjectiveFunction{objective_type}())
    return Dict("schema"=>"official-orlib-MOI-raw-binary64-v1", "variables"=>variable_rows,
        "semantic_aliases"=>aliases, "constraints"=>constraints, "typed_counts"=>typed_counts,
        "objective_sense"=>string(MOI.get(backend, MOI.ObjectiveSense())), "objective"=>raw_function(objective),
        "counts"=>Dict("all_variables"=>length(vars), "scalar_affine_rows"=>affine_rows,
                        "native_ZeroOne_constraints"=>length(binary_indices)),
        "binary_variable_indices"=>sort(binary_indices), "optimizer_state"=>"NO_OPTIMIZER",
        "semantic_aliases_complete_and_unique"=>true,
        "duplicate_rows_preserved"=>true, "mfg_omitted"=>false, "finite_boxes_added"=>false,
        "coefficient_normalization_performed"=>false, "comparison_status"=>"NOT_COMPARED")
end

function main()
    ensure(length(ARGS) == 6, "Usage: CASE_GZIP ENVIRONMENT_RECEIPT EXPECTED_RECEIPT_SHA OUTPUT_DIR PROJECT_MANIFEST EXPECTED_MANIFEST_SHA")
    case_path, env_path, env_sha, output, manifest_path, manifest_sha = abspath(ARGS[1]), abspath(ARGS[2]), ARGS[3], abspath(ARGS[4]), abspath(ARGS[5]), ARGS[6]
    ensure(!ispath(output) && isdir(dirname(output)), "Output must be new under an existing parent")
    ensure(digest(case_path) == CASE_SHA && digest(env_path) == env_sha && digest(manifest_path) == manifest_sha, "Trusted input hash mismatch")
    env_receipt = JSON.parsefile(env_path)
    ensure(env_receipt["status"] == "READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD", "Environment was not accepted")
    ensure(VERSION == v"1.6.7" && length(DEPOT_PATH) == 1, "Runtime/depot differs")
    ensure(abspath(DEPOT_PATH[1]) == abspath(env_receipt["isolated_environment"]["JULIA_DEPOT_PATH"]), "Wrong isolated depot")
    ensure(digest(joinpath(Sys.BINDIR, "julia.exe")) == env_receipt["runtime_executable_sha256"], "Runtime executable changed")
    ensure(digest(joinpath(dirname(Base.active_project()), "Manifest.toml")) == manifest_sha, "Active project manifest mismatch")
    deps = Pkg.dependencies()
    for (name, version) in EXPECTED_VERSIONS
        matches = [p for (_,p) in deps if p.name == name]
        ensure(length(matches) == 1 && only(matches).version == version, "Package version mismatch: " * name)
    end
    uc = only([p for (_,p) in deps if p.name == "UnitCommitment"])
    ensure(uc.git_revision == UC_COMMIT, "Official source revision changed")
    for item in env_receipt["pinned_native_files_verified"]
        ensure(digest(joinpath(uc.source, item["path"])) == item["sha256"], "Native source changed")
    end
    snapshot = Dict(case_path=>digest(case_path), env_path=>digest(env_path), manifest_path=>digest(manifest_path),
                    abspath(@__FILE__)=>digest(@__FILE__))
    for item in env_receipt["pinned_native_files_verified"]
        snapshot[abspath(joinpath(uc.source, item["path"]))] = item["sha256"]
    end
    mkdir(output)
    began = time_ns()
    ledger = Dict{String,Any}("started_utc"=>nowutc(), "native_read_attempts"=>0,
        "native_build_attempts"=>0, "optimizer_calls"=>0, "automatic_retry"=>false,
        "input_sha256"=>snapshot, "source_sha256"=>digest(@__FILE__))
    write_new(joinpath(output, "execution_started.json"), copy(ledger))
    try
        ledger["native_read_attempts"] = 1
        write_new(joinpath(output, "native_read_attempt.json"), copy(ledger))
        instance = UnitCommitment.read(case_path)
        write_new(joinpath(output, "official_parsed_instance.json"), parsed_instance(instance))
        ledger["native_build_attempts"] = 1
        ledger["build_started_utc"] = nowutc()
        write_new(joinpath(output, "native_build_attempt.json"), copy(ledger))
        model = UnitCommitment.build_model(instance=instance, optimizer=nothing,
            formulation=UnitCommitment.Formulation(), variable_names=true)
        ledger["build_returned_utc"] = nowutc()
        write_new(joinpath(output, "native_build_returned.json"), copy(ledger))
        raw = export_backend(model)
        write_new(joinpath(output, "official_raw_model.json"), raw)
        for (path, expected) in snapshot
            ensure(digest(path) == expected, "Frozen input changed during export")
        end
        ledger["status"] = "OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON"
        ledger["counts"] = raw["counts"]
        ledger["raw_model_sha256"] = digest(joinpath(output, "official_raw_model.json"))
        ledger["parsed_instance_sha256"] = digest(joinpath(output, "official_parsed_instance.json"))
        ledger["inputs_unchanged"] = true
    catch err
        ledger["status"] = "EXPORT_FAILED_PRESERVED_NO_RETRY"
        ledger["error"] = sprint(showerror, err)
        ledger["ended_utc"] = nowutc()
        ledger["elapsed_seconds"] = (time_ns()-began)/1e9
        write_new(joinpath(output, "failure.json"), ledger)
        rethrow()
    end
    ledger["ended_utc"] = nowutc()
    ledger["elapsed_seconds"] = (time_ns()-began)/1e9
    write_new(joinpath(output, "completion.json"), ledger)
    println(JSON.json(Dict("status"=>ledger["status"], "counts"=>ledger["counts"], "optimizer_calls"=>0)))
end

if abspath(PROGRAM_FILE) == abspath(@__FILE__)
    main()
end
