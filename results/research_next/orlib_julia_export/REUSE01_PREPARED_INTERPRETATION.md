# Reuse01 prepared interpretation

The frozen preparation `reuse_prepared01/prepared.json` has SHA256 `6113f906703d29da0177e666f1fc66eda0854efb4432ff2017197997186cc4d2`, with 36 bindings and 21 selected direct-registry metadata files. It closed once, exit 0, in 1.83 seconds. Source SHA256 is `2e1add47952cbeb1f2a26800619277623c4b8975118fe19e933b7680eea61a3a`; protocol SHA256 is `eb1f8a857ca8228bcf33b7bb85fdddf4c157d49295883c3fc52fa0b0b7b51a2b`. Julia/Pkg/network/extraction/full-registry scans were not invoked. Both prospective setup output directories were absent after preparation.

## Precision note from independent source review

The protocol phrase “Recheck all prepared/selected bindings ... at closure” needs this narrower reading of the frozen implementation. After a successful Pkg call, each resolved registered nonstdlib dependency's selected metadata is checked against the archived inventory. At final closure, the source rechecks all 36 prepared bindings, including the 21 selected direct metadata files, and rereads Registry.toml plus depot/update-marker conditions. It does **not** perform a second reread of every newly resolved transitive metadata file. No second transitive reread should be claimed.

This is a reporting clarification under the already explicit no-external-concurrent-mutation/storage-fault assumption. It changes neither the frozen source/protocol nor the admission test. The source-only independent review found no launch blocker on this point. Whole physical registry readback and blanket installed-package tree rehash remain unestablished. This note authorizes no execution; Julia/Pkg remains subject to the parent's separate source/prepared gate.
