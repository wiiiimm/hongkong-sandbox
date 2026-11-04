# Block 8: recovered terrain coverage validation

The unchanged-source disjoint preservation failed the parent-rectangle coverage assertion. A fresh measured float32 declaration qualifies the 0.01300231680118048 m² residue under the existing strict 0.25 m² maximum and 2 mm distance. Terrain position/index and government building geometry remain unchanged.

Full checks ran successfully. Seventeen disjoint basic neighbours now retain parent terrain; 29 source-overlapping neighbours remain blocked. The source still fails ground contact, terrain burial and whole-source foundation. No installation credit or threshold waiver. Exact results and released reservation are saved in Neon: `1ba0840a485df6212850a1efc8d06b9f42081bc6c3611e59cea64b3f51def815`.
