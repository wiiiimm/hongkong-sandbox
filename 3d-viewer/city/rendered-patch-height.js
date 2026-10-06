// Parent water beds and child native patches are both drawn. Query the top surface.
export function renderedPatchHeight(childHeight, waterBed, fallback) {
 if(Number.isFinite(childHeight))return Number.isFinite(waterBed)?Math.max(childHeight,waterBed):childHeight;
 return Number.isFinite(waterBed)?waterBed:fallback();
}
