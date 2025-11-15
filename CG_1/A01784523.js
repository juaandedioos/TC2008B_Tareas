// Nombre: Juan de Dios Gastelum Flores (A01784523)
// Fecha: 14/11/2025
// Descripción: Carita feliz en WebGL2 usando TWGL y M3, con transformaciones
// 2D controladas mediante una interfaz interactiva (lil-gui).

import GUI from "lil-gui";
import * as twgl from "twgl-base.js";
import { M3 } from "./2d-lib.js";

// --- Shaders ---
const vertexShaderSource = `#version 300 es
in vec2 a_position;

uniform mat3 u_matrix;
uniform vec2 u_resolution;

void main() {
  vec2 position = (u_matrix * vec3(a_position, 1)).xy;
  vec2 zeroToOne = position / u_resolution;
  vec2 zeroToTwo = zeroToOne * 2.0;
  vec2 clipSpace = zeroToTwo - 1.0;
  gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
}
`;

const fragmentShaderSource = `#version 300 es
precision highp float;
uniform vec4 u_color;
out vec4 outColor;
void main() {
  outColor = u_color;
}
`;

// UI Settings
const transformSettings = {
  pivoteTX: 200,
  pivoteTY: 200,
  caraTX: 400,
  caraTY: 300,
  caraS: 1.0,
  caraRot: 0,
};

// Colores
const headColor = [255 / 255, 220 / 255, 0 / 255, 1]; 
const featuresColor = [0 / 255, 0 / 255, 0 / 255, 1]; 
const pivoteColor = [100 / 255, 100 / 255, 100 / 255, 1]; 

// Globales
let gl, programInfo;
let caraBufferInfo, pivoteBufferInfo, bocaBufferInfo;
let caraVao, pivoteVao, bocaVao;

// --- Main ---
function main() {
  gl = document.querySelector("#canvas").getContext("webgl2");
  if (!gl) {
    console.error("WebGL 2 no disponible");
    return;
  }

  programInfo = twgl.createProgramInfo(gl, [
    vertexShaderSource,
    fragmentShaderSource,
  ]);

  const caraArrays = createCaraGeometry();
  const pivoteArrays = createPivoteGeometry();
  const bocaArrays = createBocaGeometry();

  caraBufferInfo = twgl.createBufferInfoFromArrays(gl, caraArrays);
  pivoteBufferInfo = twgl.createBufferInfoFromArrays(gl, pivoteArrays);
  bocaBufferInfo = twgl.createBufferInfoFromArrays(gl, bocaArrays);

  caraVao = twgl.createVAOFromBufferInfo(gl, programInfo, caraBufferInfo);
  pivoteVao = twgl.createVAOFromBufferInfo(gl, programInfo, pivoteBufferInfo);
  bocaVao = twgl.createVAOFromBufferInfo(gl, programInfo, bocaBufferInfo);

  setupUI();
  requestAnimationFrame(drawScene);
}

// --- UI ---
function setupUI() {
  const gui = new GUI();
  gui.add(transformSettings, "pivoteTX", 0, 800).name("Pivote X");
  gui.add(transformSettings, "pivoteTY", 0, 600).name("Pivote Y");
  gui.add(transformSettings, "caraTX", 0, 800).name("Cara X");
  gui.add(transformSettings, "caraTY", 0, 600).name("Cara Y");
  gui.add(transformSettings, "caraS", 0.1, 5.0).name("Cara Escala");
  gui.add(transformSettings, "caraRot", 0, 360).name("Cara Rotación");
}

// --- Render Loop ---
function drawScene() {
  twgl.resizeCanvasToDisplaySize(gl.canvas);
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
  gl.clearColor(1, 1, 1, 1);
  gl.clear(gl.COLOR_BUFFER_BIT);

  gl.useProgram(programInfo.program);

  // --- Pivote ---
  {
    gl.bindVertexArray(pivoteVao);
    const matrix = M3.translation([
      transformSettings.pivoteTX,
      transformSettings.pivoteTY,
    ]);
    twgl.setUniforms(programInfo, {
      u_matrix: matrix,
      u_color: pivoteColor,
      u_resolution: [gl.canvas.width, gl.canvas.height],
    });
    twgl.drawBufferInfo(gl, pivoteBufferInfo);
  }

  // --- Matriz Base de la Cara ---
  const rotRad = (transformSettings.caraRot * Math.PI) / 180;
  const scaleMatrix = M3.scaling([
    transformSettings.caraS,
    transformSettings.caraS,
  ]);
  const translationMatrix = M3.translation([
    transformSettings.caraTX,
    transformSettings.caraTY,
  ]);
  const toPivotMatrix = M3.translation([
    transformSettings.pivoteTX,
    transformSettings.pivoteTY,
  ]);
  const rotationMatrix = M3.rotation(rotRad);
  const fromPivotMatrix = M3.translation([
    -transformSettings.pivoteTX,
    -transformSettings.pivoteTY,
  ]);

  let caraMatrix = M3.identity();
  caraMatrix = M3.multiply(caraMatrix, toPivotMatrix);
  caraMatrix = M3.multiply(caraMatrix, rotationMatrix);
  caraMatrix = M3.multiply(caraMatrix, fromPivotMatrix);
  caraMatrix = M3.multiply(caraMatrix, translationMatrix);
  caraMatrix = M3.multiply(caraMatrix, scaleMatrix);

  // --- Cara ---
  {
    gl.bindVertexArray(caraVao);
    twgl.setUniforms(programInfo, {
      u_matrix: caraMatrix,
      u_color: headColor,
      u_resolution: [gl.canvas.width, gl.canvas.height],
    });
    twgl.drawBufferInfo(gl, caraBufferInfo);
  }

  // --- Ojos ---
  {
    gl.bindVertexArray(pivoteVao);
    const eyeScaleMatrix = M3.scaling([0.4, 0.6]);

    // Ojo izquierdo
    const eyeLeftTranslation = M3.translation([-20, -15]);
    let eyeLeftMatrix = M3.multiply(eyeLeftTranslation, eyeScaleMatrix);
    eyeLeftMatrix = M3.multiply(caraMatrix, eyeLeftMatrix);

    twgl.setUniforms(programInfo, {
      u_matrix: eyeLeftMatrix,
      u_color: featuresColor,
      u_resolution: [gl.canvas.width, gl.canvas.height],
    });
    twgl.drawBufferInfo(gl, pivoteBufferInfo);

    // Ojo derecho
    const eyeRightTranslation = M3.translation([20, -15]); 
    let eyeRightMatrix = M3.multiply(eyeRightTranslation, eyeScaleMatrix);
    eyeRightMatrix = M3.multiply(caraMatrix, eyeRightMatrix);

    twgl.setUniforms(programInfo, {
      u_matrix: eyeRightMatrix,
      u_color: featuresColor,
      u_resolution: [gl.canvas.width, gl.canvas.height],
    });
    twgl.drawBufferInfo(gl, pivoteBufferInfo);
  }

  // --- Boca ---
  {
    gl.bindVertexArray(bocaVao);
    const mouthTranslation = M3.translation([0, 20]);
    const mouthMatrix = M3.multiply(caraMatrix, mouthTranslation);

    twgl.setUniforms(programInfo, {
      u_matrix: mouthMatrix,
      u_color: featuresColor,
      u_resolution: [gl.canvas.width, gl.canvas.height],
    });
    twgl.drawBufferInfo(gl, bocaBufferInfo, gl.TRIANGLES);
  }

  requestAnimationFrame(drawScene);
}

// --- Geometrías ---

function createCaraGeometry() {
  const radius = 50;
  const segments = 24;
  const positions = [0, 0];

  for (let i = 0; i <= segments; i++) {
    const angle = (i / segments) * 2 * Math.PI;
    positions.push(Math.cos(angle) * radius, Math.sin(angle) * radius);
  }

  const indices = [];
  for (let i = 1; i < segments + 1; i++) {
    indices.push(0, i, i + 1);
  }

  return {
    a_position: { numComponents: 2, data: positions },
    indices: { numComponents: 3, data: indices },
  };
}

function createPivoteGeometry() {
  const s = 15;
  return {
    a_position: { numComponents: 2, data: [0, -s, s, 0, -s, 0, 0, s] },
    indices: { numComponents: 3, data: [0, 1, 2, 2, 1, 3] },
  };
}

function createBocaGeometry() {
  const w = 25; 
  const h = 15;

  return {
    a_position: {
      numComponents: 2,
      data: [
        -w,
        -h,
        w,
        -h,
        0,
        h,
      ],
    },
    indices: { numComponents: 3, data: [0, 1, 2] },
  };
}

main();
