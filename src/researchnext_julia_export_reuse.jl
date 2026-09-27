# Prospective reuse01 official export. No optimizer attachment or optimize! call.
# Scientific imports precede main: a separately reviewed launcher must first
# admit the frozen READY receipt/Manifest/paths/source bytes. Internal checks
# protect the subsequent native read and build; they are not pre-import guards.
using Pkg, SHA, Dates, TOML
using UnitCommitment, JuMP, MathOptInterface
const MOI = MathOptInterface
# JSON is an installed dependency of the pinned native package, not a new direct
# dependency of the isolated project. Use its already declared module binding.
const JSON = UnitCommitment.JSON

const CASE_SHA = "6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe"
const UC_COMMIT = "4f04f0dd6641b071fd7556346c3d7190c2ffdfe5"
const UC_TREE = "619a6b12e1005425e6ac08c4c45e445bb0a6f134"
const SETUP_SOURCE_SHA = "2e1add47952cbeb1f2a26800619277623c4b8975118fe19e933b7680eea61a3a"
const SETUP_PROTOCOL_SHA = "eb1f8a857ca8228bcf33b7bb85fdddf4c157d49295883c3fc52fa0b0b7b51a2b"
const SETUP_PREPARED_SHA = "6113f906703d29da0177e666f1fc66eda0854efb4432ff2017197997186cc4d2"
const PARENT_EXPORT_SHA = "e7429f67a3d984976c84081acb3845dbd1238f198afb21b49266d87fae3d9088"
const REPOSITORY = abspath(joinpath(@__DIR__, ".."))
const REUSE_ROOT = joinpath(REPOSITORY, ".work", "researchnext_julia_export", "setup_reuse01")
const SECONDARY_DEPOT = joinpath(REPOSITORY, ".work", "researchnext_julia_export", "setup_efficient01", "depot")
const EXPECTED_RECEIPT = joinpath(REPOSITORY, "results", "research_next", "orlib_julia_export", "setup_reuse01", "ENVIRONMENT_ACQUISITION.json")
const EXPECTED_OUTPUT = joinpath(REPOSITORY, "results", "research_next", "orlib_julia_export", "official_export_reuse01")
const EXPORT_PROTOCOL = joinpath(REPOSITORY,"docs","research_next","ORLIB_JULIA_REUSE_EXPORT_PROTOCOL.md")
pathkey(p) = Sys.iswindows() ? lowercase(normpath(abspath(p))) : normpath(abspath(p))
samepath(a,b) = pathkey(a) == pathkey(b)
function underpath(path, root)
    p, r = pathkey(path), pathkey(root)
    return p == r || startswith(p, r * (Sys.iswindows() ? "\\" : "/"))
end

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
    ensure(samepath(output, EXPECTED_OUTPUT) && samepath(env_path, EXPECTED_RECEIPT), "Wrong path-bound reuse01 output/receipt")
    ensure(samepath(manifest_path, joinpath(REUSE_ROOT,"project","Manifest.toml")), "Wrong actual reuse01 Manifest path")
    ensure(digest(case_path) == CASE_SHA && digest(env_path) == env_sha && digest(manifest_path) == manifest_sha, "Trusted input hash mismatch")
    env_receipt = JSON.parsefile(env_path)
    ensure(env_receipt["status"] == "READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD", "Environment was not accepted")
    ensure(env_receipt["julia_exit_code"]==0 && env_receipt["Julia_invocations"]==1 && env_receipt["Pkg_add_calls"]==1 && isempty(env_receipt["stream_errors"]), "Setup did not close normally")
    ensure(env_receipt["source_sha256"] == SETUP_SOURCE_SHA && env_receipt["protocol_sha256"] == SETUP_PROTOCOL_SHA && env_receipt["prepared_sha256"] == SETUP_PREPARED_SHA, "Wrong frozen reuse setup")
    ensure(env_receipt["source_unchanged_at_closure"] && env_receipt["protocol_unchanged_at_closure"] && env_receipt["admitted_archive_unchanged_at_closure"], "Setup bindings did not close unchanged")
    ensure(env_receipt["scientific_model_builds"] == 0 && env_receipt["optimizer_calls"] == 0, "Unexpected prior scientific calls")
    ensure(!env_receipt["whole_disk_registry_readback_completed"], "Unexpected inherited provenance contract")
    ensure(env_receipt["Windows_installed_archive_full_tree_verification"] == "NOT_ESTABLISHED_BY_PKG_INSTALL_ARCHIVE", "Missing Windows tree-hash caveat")
    ensure(VERSION == v"1.6.7" && length(DEPOT_PATH) == 2, "Runtime/depot differs")
    expected_depots = [joinpath(REUSE_ROOT,"depot"), SECONDARY_DEPOT]
    ensure(all(samepath(a,b) for (a,b) in zip(DEPOT_PATH,expected_depots)), "Wrong ordered isolated depots")
    receipt_depots = split(env_receipt["isolated_environment"]["JULIA_DEPOT_PATH"],';',keepempty=true)
    ensure(length(receipt_depots)==2 && all(samepath(a,b) for (a,b) in zip(receipt_depots,expected_depots)), "Receipt depot path mismatch")
    ensure(samepath(Base.active_project(), joinpath(REUSE_ROOT,"project","Project.toml")), "Wrong active project")
    ensure(get(ENV,"JULIA_LOAD_PATH","")=="@;@stdlib" && get(ENV,"JULIA_PKG_SERVER","unset")=="", "Unexpected process-local environment")
    ensure(get(ENV,"JULIA_NUM_THREADS","")=="1" && get(ENV,"OPENBLAS_NUM_THREADS","")=="1", "Unexpected thread environment")
    artifact_sha = Dict(item["path"]=>item["sha256"] for item in env_receipt["artifacts"])
    for leaf in ("Project.toml","Manifest.toml")
        ensure(digest(joinpath(REUSE_ROOT,"project",leaf))==artifact_sha[leaf] && digest(joinpath(dirname(env_path),leaf))==artifact_sha[leaf], "Actual/archived project metadata changed")
    end
    ensure(artifact_sha["Manifest.toml"]==manifest_sha, "Manifest external/receipt pin mismatch")
    inventory_path = joinpath(REUSE_ROOT,"package_inventory.toml")
    ensure(digest(inventory_path)==artifact_sha["package_inventory.toml"] && digest(joinpath(dirname(env_path),"package_inventory.toml"))==artifact_sha["package_inventory.toml"], "Package inventory changed")
    installed_inventory = TOML.parsefile(inventory_path)
    selected_meta_path = joinpath(dirname(env_path),"selected_registry_and_installed_metadata.json")
    ensure(digest(selected_meta_path)==artifact_sha["selected_registry_and_installed_metadata.json"], "Selected metadata receipt changed")
    selected_meta = JSON.parsefile(selected_meta_path)
    for item in selected_meta["selected_registry_metadata"]
        ensure(underpath(item["path"],joinpath(SECONDARY_DEPOT,"registries","General")) && digest(item["path"])==item["sha256"], "Selected actual registry metadata changed")
    end
    ensure(!ispath(joinpath(SECONDARY_DEPOT,"registries","General",".git")) && !ispath(joinpath(SECONDARY_DEPOT,"registries","General",".tree_info.toml")), "Unexpected registry update marker")
    ensure(digest(joinpath(Sys.BINDIR, "julia.exe")) == env_receipt["runtime_executable_sha256"], "Runtime executable changed")
    ensure(digest(joinpath(dirname(Base.active_project()), "Manifest.toml")) == manifest_sha, "Active project manifest mismatch")
    deps = Pkg.dependencies()
    for (name, version) in EXPECTED_VERSIONS
        matches = [p for (_,p) in deps if p.name == name]
        ensure(length(matches) == 1 && only(matches).version == version, "Package version mismatch: " * name)
    end
    uc = only([p for (_,p) in deps if p.name == "UnitCommitment"])
    ensure(uc.git_revision == UC_COMMIT && string(uc.tree_hash)==UC_TREE, "Official source revision/tree changed")
    ensure(samepath(uc.source, env_receipt["selected_package"]["source"]), "Native source location changed")
    recorded_packages = Dict(item["uuid"]=>item for item in installed_inventory["packages"])
    ensure(length(deps)==length(recorded_packages), "Resolved dependency roster changed")
    for (uuid,p) in deps
        row = recorded_packages[string(uuid)]
        ensure(row["name"]==p.name && row["version"]==(p.version===nothing ? "" : string(p.version)), "Resolved dependency identity changed")
        ensure(row["tree_hash"]==(p.tree_hash===nothing ? "" : string(p.tree_hash)) && samepath(row["source"],p.source), "Resolved dependency tree/source changed")
        if Pkg.Types.is_stdlib(uuid)
            ensure(row["is_stdlib"] && underpath(p.source,joinpath(Sys.BINDIR,"..","share","julia","stdlib")), "Wrong stdlib source")
        else
            ensure(!row["is_stdlib"] && underpath(p.source,joinpath(REUSE_ROOT,"depot","packages")), "Wrong installed package source")
        end
    end
    for (mod,name) in ((UnitCommitment,"UnitCommitment"),(JuMP,"JuMP"),(MathOptInterface,"MathOptInterface"))
        package=only([p for (_,p) in deps if p.name==name])
        ensure(underpath(pathof(mod),package.source), "Loaded module outside reported source: " * name)
    end
    ensure(length(env_receipt["pinned_native_files_verified"])==18, "Wrong native source binding count")
    ensure(length(unique([item["path"] for item in env_receipt["pinned_native_files_verified"]]))==18, "Duplicate native source binding")
    for item in env_receipt["pinned_native_files_verified"]
        ensure(digest(joinpath(uc.source, item["path"])) == item["sha256"], "Native source changed")
    end
    snapshot = Dict(case_path=>digest(case_path), env_path=>digest(env_path), manifest_path=>digest(manifest_path),
                    abspath(@__FILE__)=>digest(@__FILE__),
                    abspath(Base.active_project())=>digest(Base.active_project()),
                    abspath(inventory_path)=>digest(inventory_path),
                    abspath(selected_meta_path)=>digest(selected_meta_path),
                    abspath(EXPORT_PROTOCOL)=>digest(EXPORT_PROTOCOL))
    for item in selected_meta["selected_registry_metadata"]
        snapshot[abspath(item["path"])]=item["sha256"]
    end
    for mod in (UnitCommitment,JuMP,MathOptInterface)
        snapshot[abspath(pathof(mod))]=digest(pathof(mod))
    end
    for item in env_receipt["pinned_native_files_verified"]
        snapshot[abspath(joinpath(uc.source, item["path"]))] = item["sha256"]
    end
    mkdir(output)
    began = time_ns()
    ledger = Dict{String,Any}("started_utc"=>nowutc(), "native_read_attempts"=>0,
        "native_build_attempts"=>0, "optimizer_calls"=>0, "automatic_retry"=>false,
        "input_sha256"=>snapshot, "source_sha256"=>digest(@__FILE__),
        "parent_export_source_sha256"=>PARENT_EXPORT_SHA,
        "setup_prepared_sha256"=>SETUP_PREPARED_SHA,
        "depot_path"=>copy(DEPOT_PATH),
        "whole_disk_registry_readback_completed"=>false,
        "whole_installed_package_tree_rehash"=>false,
        "scientific_imports_precede_internal_main_guards"=>true,
        "external_prelaunch_gate_required"=>true)
    write_new(joinpath(output, "execution_started.json"), copy(ledger))
    try
        ledger["native_read_attempts"] = 1
        ledger["native_read_started_utc"] = nowutc()
        ledger["native_read_started_unix_seconds"] = time()
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
