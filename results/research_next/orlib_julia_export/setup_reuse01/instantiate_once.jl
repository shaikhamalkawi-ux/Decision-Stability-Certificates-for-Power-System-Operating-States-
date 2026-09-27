function durable_stage(s)
    msg=string(s," unix_seconds=",time())
    open(joinpath(dirname(ARGS[2]),"julia_stages.log"),"a") do io
        println(io,msg); flush(io)
    end
    println(stderr,msg); flush(stderr)
end
durable_stage("BEFORE_PKG_IMPORT")
using Pkg, TOML, Dates, Logging
durable_stage("AFTER_PKG_IMPORT")
@assert VERSION == v"1.6.7"
@assert length(DEPOT_PATH) == 2
@assert abspath(DEPOT_PATH[2]) == abspath(ARGS[3])
@assert abspath(DEPOT_PATH[1]) == abspath(ARGS[1])
@assert get(ENV,"JULIA_PKG_SERVER","unset") == ""
function stage(s)
    durable_stage(s)
end
global_logger(ConsoleLogger(stderr))
stage("PKG_TOML_IMPORT_COMPLETE")
@assert isfile(joinpath(DEPOT_PATH[2],"registries","General","Registry.toml"))
@assert isempty(Pkg.Types.collect_registries(DEPOT_PATH[1]))
@assert length(Pkg.Types.collect_registries()) == 1
specs=[PackageSpec(url="https://github.com/ANL-CEEESA/UnitCommitment.jl",rev="4f04f0dd6641b071fd7556346c3d7190c2ffdfe5"),
       PackageSpec(name="JuMP",version=v"1.15.1"),
       PackageSpec(name="MathOptInterface",version=v"1.20.1"),
       PackageSpec(name="PackageCompiler",version=v"1.7.7")]
open(joinpath(dirname(ARGS[2]),"pkg_add_started.txt"),"w") do io
    println(io,"One Pkg.add attempt; ",Dates.now(Dates.UTC)); flush(io)
end
stage("PKG_ADD_ATTEMPT")
Pkg.add(specs)
stage("PKG_ADD_RETURNED")
deps=Pkg.dependencies()
expected=Dict("UnitCommitment"=>v"0.4.0","JuMP"=>v"1.15.1","MathOptInterface"=>v"1.20.1","PackageCompiler"=>v"1.7.7")
rows=Any[]
for (uuid,p) in deps
    if haskey(expected,p.name)
        @assert p.version==expected[p.name]; delete!(expected,p.name)
    end
    row=Dict{String,Any}("uuid"=>string(uuid),"name"=>p.name,
        "version"=>(p.version===nothing ? "" : string(p.version)),
        "tree_hash"=>(p.tree_hash===nothing ? "" : string(p.tree_hash)),
        "source"=>(p.source===nothing ? "" : string(p.source)),"direct"=>p.is_direct_dep,
        "is_stdlib"=>Pkg.Types.is_stdlib(uuid))
    for key in (:git_revision,:git_source,:is_tracking_repo,:is_tracking_path)
        if hasproperty(p,key)
            v=getproperty(p,key); row[string(key)]=v===nothing ? "" : string(v)
        end
    end
    push!(rows,row)
end
@assert isempty(expected)
sort!(rows,by=x->x["name"])
open(ARGS[2],"w") do io
    TOML.print(io,Dict("julia_version"=>string(VERSION),"machine"=>Sys.MACHINE,
      "active_project"=>Base.active_project(),"depot_path"=>DEPOT_PATH,"packages"=>rows))
end
stage("DEPENDENCY_INVENTORY_CLOSED_NO_SCIENTIFIC_IMPORT")
