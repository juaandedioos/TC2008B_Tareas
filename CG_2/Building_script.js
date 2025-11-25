/*
 * Nombre: Juan de Dios Gastélum Flores
 * Matricula: A01784523
 * Descripcion: Script para generar modelos 3D de edificios en formato OBJ.
 * Calcula vertices, normales y caras triangulares.
 */

const X = 0, Y = 1, Z = 2;

class V3 {
    static create(x, y, z) {
        const v = new Float32Array(3);
        v[X] = x;
        v[Y] = y;
        v[Z] = z;
        return v;
    }

    static subtract(u, v, dest) {
        dest = dest || new Float32Array(3);
        dest[X] = u[X] - v[X];
        dest[Y] = u[Y] - v[Y];
        dest[Z] = u[Z] - v[Z];
        return dest;
    }

    static cross(u, v, dest) {
        dest = dest || new Float32Array(3);
        dest[X] = u[Y] * v[Z] - u[Z] * v[Y];
        dest[Y] = u[Z] * v[X] - u[X] * v[Z];
        dest[Z] = u[X] * v[Y] - u[Y] * v[X];
        return dest;
    }

    static normalize(v, dest) {
        dest = dest || new Float32Array(3);
        const size = Math.sqrt(v[X]*v[X] + v[Y]*v[Y] + v[Z]*v[Z]);
        if (size > 0) {
            dest[X] = v[X] / size;
            dest[Y] = v[Y] / size;
            dest[Z] = v[Z] / size;
        } else {
            dest[X] = dest[Y] = dest[Z] = 0;
        }
        return dest;
    }
}

function clampSides(sides) {
    return Math.max(3, Math.min(36, sides));
}

function parseArgs() {
    const args = process.argv.slice(2);
    let sides = parseInt(args[0]);
    let height = parseFloat(args[1]);
    let rBase = parseFloat(args[2]);
    let rTop = args[3] !== undefined ? parseFloat(args[3]) : 0.8;

    if (!Number.isFinite(sides)) sides = 8;
    if (!Number.isFinite(height)) height = 6.0;
    if (!Number.isFinite(rBase)) rBase = 1.0;
    if (!Number.isFinite(rTop)) rTop = 0.8;

    sides = clampSides(sides);
    return { sides, height, rBase, rTop };
}

function addVertexWithNormal(vertices, normals, vx, vy, vz, nx, ny, nz) {
    const v = V3.create(vx, vy, vz);
    const n = V3.create(nx, ny, nz);
    vertices.push(v);
    normals.push(n);
    return vertices.length; 
}

function buildSides(vertices, normals, faces, sides, height, rBase, rTop) {
    const angleStep = (Math.PI * 2) / sides;

    const topIndex = [];
    const bottomIndex = [];

    for (let i = 0; i < sides; i++) {
        const theta = i * angleStep;
        const cosTheta = Math.cos(theta);
        const sinTheta = Math.sin(theta);

        const xBottom = rBase * cosTheta;
        const zBottom = rBase * sinTheta;
        const xTop = rTop * cosTheta;
        const zTop = rTop * sinTheta;

        const vBottom = V3.create(xBottom, 0, zBottom);
        const vTop = V3.create(xTop, height, zTop);

        const up = V3.subtract(vTop, vBottom);
        const tangent = V3.create(-sinTheta, 0, cosTheta);
        let sideNormal = V3.cross(up, tangent);
        sideNormal = V3.normalize(sideNormal, sideNormal);

        const idxTop = addVertexWithNormal(
            vertices, normals,
            xTop, height, zTop,
            sideNormal[X], sideNormal[Y], sideNormal[Z]
        );
        const idxBottom = addVertexWithNormal(
            vertices, normals,
            xBottom, 0, zBottom,
            sideNormal[X], sideNormal[Y], sideNormal[Z]
        );

        topIndex.push(idxTop);
        bottomIndex.push(idxBottom);
    }

    for (let i = 0; i < sides; i++) {
        const next = (i + 1) % sides;

        const currTop = topIndex[i];
        const currBot = bottomIndex[i];
        const nextTop = topIndex[next];
        const nextBot = bottomIndex[next];

        faces.push([currBot, nextBot, currTop]);
        faces.push([nextBot, nextTop, currTop]);
    }
}

function buildTopCap(vertices, normals, faces, sides, height, rTop) {
    const angleStep = (Math.PI * 2) / sides;

    const centerIndex = addVertexWithNormal(vertices, normals, 0, height, 0, 0, 1, 0);
    const rimIndex = [];

    for (let i = 0; i < sides; i++) {
        const theta = i * angleStep;
        const x = rTop * Math.cos(theta);
        const z = rTop * Math.sin(theta);
        const idx = addVertexWithNormal(vertices, normals, x, height, z, 0, 1, 0);
        rimIndex.push(idx);
    }

    for (let i = 0; i < sides; i++) {
        const next = (i + 1) % sides;
        const current = rimIndex[i];
        const nextIdx = rimIndex[next];
        faces.push([centerIndex, nextIdx, current]);
    }
}

function buildBottomCap(vertices, normals, faces, sides, rBase) {
    const angleStep = (Math.PI * 2) / sides;

    const centerIndex = addVertexWithNormal(vertices, normals, 0, 0, 0, 0, -1, 0);
    const rimIndex = [];

    for (let i = 0; i < sides; i++) {
        const theta = i * angleStep;
        const x = rBase * Math.cos(theta);
        const z = rBase * Math.sin(theta);
        const idx = addVertexWithNormal(vertices, normals, x, 0, z, 0, -1, 0);
        rimIndex.push(idx);
    }

    for (let i = 0; i < sides; i++) {
        const next = (i + 1) % sides;
        const current = rimIndex[i];
        const nextIdx = rimIndex[next];
        faces.push([centerIndex, current, nextIdx]);
    }
}

function buildBuilding(sides, height, rBase, rTop) {
    const vertices = [];
    const normals = [];
    const faces = [];

    buildSides(vertices, normals, faces, sides, height, rBase, rTop);
    buildTopCap(vertices, normals, faces, sides, height, rTop);
    buildBottomCap(vertices, normals, faces, sides, rBase);

    return { vertices, normals, faces };
}

function buildOBJString(sides, height, rBase, rTop, vertices, normals, faces) {
    let obj = '';
    obj += `# Building: Sides=${sides}, Height=${height}, R_Base=${rBase}, R_Top=${rTop}\n`;
    obj += `o Building_${sides}_${height}_${rBase}_${rTop}\n`;

    for (let i = 0; i < vertices.length; i++) {
        const v = vertices[i];
        obj += `v ${v[X].toFixed(4)} ${v[Y].toFixed(4)} ${v[Z].toFixed(4)}\n`;
    }

    obj += '\n';

    for (let i = 0; i < normals.length; i++) {
        const n = normals[i];
        obj += `vn ${n[X].toFixed(4)} ${n[Y].toFixed(4)} ${n[Z].toFixed(4)}\n`;
    }

    obj += '\n';

    for (let i = 0; i < faces.length; i++) {
        const a = faces[i][0];
        const b = faces[i][1];
        const c = faces[i][2];
        obj += `f ${a}//${a} ${b}//${b} ${c}//${c}\n`;
    }

    return obj;
}

function main() {
    const { sides, height, rBase, rTop } = parseArgs();
    const { vertices, normals, faces } = buildBuilding(sides, height, rBase, rTop);
    const objContent = buildOBJString(sides, height, rBase, rTop, vertices, normals, faces);
    console.log(objContent);
}

main();