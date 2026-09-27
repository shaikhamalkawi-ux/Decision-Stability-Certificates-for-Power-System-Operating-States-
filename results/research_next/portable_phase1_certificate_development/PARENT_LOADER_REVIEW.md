# Parent review of verified-source loading change

The new loader in source8a1774b6ab342abf60e2b21f673f56905cc07d66c5eb283ce350703c0976e625 was read independently of its author. It reads decoder source bytes once, compares their SHA256 to the fixed reviewed digest, then compile/execs those bytes in a registered module. It does not execute the SourceFileLoader or adjacent bytecode. The four-line source-loading change preserves mathematical reconstruction; the invented cache control documents the old failure and new behavior. Accepted for the new portable smoke test.

Bundle MANIFEST.json SHA256 d67b8c7733b3cdfbf2beef8350be2526fa8ebc7e161eb024481618e02fa02272 binds10 required payload files,5,237,191bytes excluding the manifest. The command will be run in a fresh copied folder with Python -I -S and no solver. This is a same-host packaging check, not independent-machine replication or new research evidence.
