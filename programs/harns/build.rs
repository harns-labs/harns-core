//! Build script for the Harns Anchor program.
//! This is a no-op build script required by some Anchor setups.

fn main() {
    {
        // Anchor programs may need a build.rs for IDL generation.
        // This file intentionally left minimal.
        println!("cargo:rerun-if-changed=src/");
    }
}
