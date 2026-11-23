// LDraw geometry attribution and transformation notes are in CREDITS.md.
const base = new URL('./', import.meta.url);

async function resource(name) {
  const response = await fetch(new URL(name, base));
  if (!response.ok) throw new Error(`Cannot load part geometry (${response.status}): ${name}`);
  return response;
}

export async function loadPartGeometries(THREE) {
  const [catalog, buffer] = await Promise.all([
    resource('index.json').then(response => response.json()),
    resource('geometry.bin').then(response => response.arrayBuffer())
  ]);
  const geometries = new Map();
  for (const [id, entry] of Object.entries(catalog)) {
    const [positionOffset, normalOffset, indexOffset] = entry.offsets;
    const packed = new Int16Array(buffer, positionOffset, entry.vertices * 3);
    const positions = Float32Array.from(packed, value => value / 2048);
    const normals = new Int8Array(buffer, normalOffset, entry.vertices * 3);
    const IndexArray = entry.indexBytes === 2 ? Uint16Array : Uint32Array;
    const indices = new IndexArray(buffer, indexOffset, entry.indices);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3, true));
    geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
    geometries.set(id, geometry);
  }
  return geometries;
}
