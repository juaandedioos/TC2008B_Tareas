/*
 * Functions for 2D transformations
 *
 * Gilberto Echeverria
 * 2024-11-04
 */

class V2 {
  static create(px, py) {
    let v = new Float32Array(2);
    v[0] = px;
    v[1] = py;
    return v;
  }
}

class M3 {
  static identity() {
    return new Float32Array([1, 0, 0, 0, 1, 0, 0, 0, 1]);
  }

  static translation(vt) {
    const tx = vt[0] || 0;
    const ty = vt[1] || 0;
    return new Float32Array([1, 0, 0, 0, 1, 0, tx, ty, 1]);
  }

  static rotation(angleRadians) {
    const c = Math.cos(angleRadians);
    const s = Math.sin(angleRadians);
    return new Float32Array([c, s, 0, -s, c, 0, 0, 0, 1]);
  }

  static scaling(vs) {
    const sx = vs[0] || 1;
    const sy = vs[1] || 1;
    return new Float32Array([sx, 0, 0, 0, sy, 0, 0, 0, 1]);
  }

  /*
    // Matrix guide (column-major):
    a00 a10 a20   (índices 0, 1, 2)
    a01 a11 a21   (índices 3, 4, 5)
    a02 a12 a22   (índices 6, 7, 8)
    */
  static multiply(ma, mb) {
    const ma00 = ma[0];
    const ma10 = ma[1];
    const ma20 = ma[2];
    const ma01 = ma[3];
    const ma11 = ma[4];
    const ma21 = ma[5];
    const ma02 = ma[6];
    const ma12 = ma[7];
    const ma22 = ma[8];

    const mb00 = mb[0];
    const mb10 = mb[1];
    const mb20 = mb[2];
    const mb01 = mb[3];
    const mb11 = mb[4];
    const mb21 = mb[5];
    const mb02 = mb[6];
    const mb12 = mb[7];
    const mb22 = mb[8];

    return new Float32Array([
      ma00 * mb00 + ma01 * mb10 + ma02 * mb20,
      ma10 * mb00 + ma11 * mb10 + ma12 * mb20,
      ma20 * mb00 + ma21 * mb10 + ma22 * mb20,
      ma00 * mb01 + ma01 * mb11 + ma02 * mb21,
      ma10 * mb01 + ma11 * mb11 + ma12 * mb21,
      ma20 * mb01 + ma21 * mb11 + ma22 * mb21,
      ma00 * mb02 + ma01 * mb12 + ma02 * mb22,
      ma10 * mb02 + ma11 * mb12 + ma12 * mb22,
      ma20 * mb02 + ma21 * mb12 + ma22 * mb22,
    ]);
  }
}

export { V2, M3 };