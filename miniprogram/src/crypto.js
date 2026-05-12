// MD5 implementation (compact, no external deps)
function safeAdd(x, y) {
  const lsw = (x & 0xffff) + (y & 0xffff)
  return (((x >> 16) + (y >> 16) + (lsw >> 16)) << 16) | (lsw & 0xffff)
}
function bitRotateLeft(num, cnt) { return (num << cnt) | (num >>> (32 - cnt)) }
function md5cmn(q, a, b, x, s, t) { return safeAdd(bitRotateLeft(safeAdd(safeAdd(a, q), safeAdd(x, t)), s), b) }
function md5ff(a, b, c, d, x, s, t) { return md5cmn((b & c) | (~b & d), a, b, x, s, t) }
function md5gg(a, b, c, d, x, s, t) { return md5cmn((b & d) | (c & ~d), a, b, x, s, t) }
function md5hh(a, b, c, d, x, s, t) { return md5cmn(b ^ c ^ d, a, b, x, s, t) }
function md5ii(a, b, c, d, x, s, t) { return md5cmn(c ^ (b | ~d), a, b, x, s, t) }

function binlMD5(x, len) {
  x[len >> 5] |= 0x80 << (len % 32)
  x[(((len + 64) >>> 9) << 4) + 14] = len
  let a = 1732584193, b = -271733879, c = -1732584194, d = 271733878
  for (let i = 0; i < x.length; i += 16) {
    const oa = a, ob = b, oc = c, od = d
    a = md5ff(a, b, c, d, x[i], 7, -680876936)
    d = md5ff(d, a, b, c, x[i + 1], 12, -389564586)
    c = md5ff(c, d, a, b, x[i + 2], 17, 606105819)
    b = md5ff(b, c, d, a, x[i + 3], 22, -1044525330)
    a = md5ff(a, b, c, d, x[i + 4], 7, -176418897)
    d = md5ff(d, a, b, c, x[i + 5], 12, 1200080426)
    c = md5ff(c, d, a, b, x[i + 6], 17, -1473231341)
    b = md5ff(b, c, d, a, x[i + 7], 22, -45705983)
    a = md5ff(a, b, c, d, x[i + 8], 7, 1770035416)
    d = md5ff(d, a, b, c, x[i + 9], 12, -1958414417)
    c = md5ff(c, d, a, b, x[i + 10], 17, -42063)
    b = md5ff(b, c, d, a, x[i + 11], 22, -1990404162)
    a = md5ff(a, b, c, d, x[i + 12], 7, 1804603682)
    d = md5ff(d, a, b, c, x[i + 13], 12, -40341101)
    c = md5ff(c, d, a, b, x[i + 14], 17, -1502002290)
    b = md5ff(b, c, d, a, x[i + 15], 22, 1236535329)
    a = md5gg(a, b, c, d, x[i + 1], 5, -165796510)
    d = md5gg(d, a, b, c, x[i + 6], 9, -1069501632)
    c = md5gg(c, d, a, b, x[i + 11], 14, 643717713)
    b = md5gg(b, c, d, a, x[i], 20, -373897302)
    a = md5gg(a, b, c, d, x[i + 5], 5, -701558691)
    d = md5gg(d, a, b, c, x[i + 10], 9, 38016083)
    c = md5gg(c, d, a, b, x[i + 15], 14, -660478335)
    b = md5gg(b, c, d, a, x[i + 4], 20, -405537848)
    a = md5gg(a, b, c, d, x[i + 9], 5, 568446438)
    d = md5gg(d, a, b, c, x[i + 14], 9, -1019803690)
    c = md5gg(c, d, a, b, x[i + 3], 14, -187363961)
    b = md5gg(b, c, d, a, x[i + 8], 20, 1163531501)
    a = md5gg(a, b, c, d, x[i + 13], 5, -1444681467)
    d = md5gg(d, a, b, c, x[i + 2], 9, -51403784)
    c = md5gg(c, d, a, b, x[i + 7], 14, 1735328473)
    b = md5gg(b, c, d, a, x[i + 12], 20, -1926607734)
    a = md5hh(a, b, c, d, x[i + 5], 4, -378558)
    d = md5hh(d, a, b, c, x[i + 8], 11, -2022574463)
    c = md5hh(c, d, a, b, x[i + 11], 16, 1839030562)
    b = md5hh(b, c, d, a, x[i + 14], 23, -35309556)
    a = md5hh(a, b, c, d, x[i + 1], 4, -1530992060)
    d = md5hh(d, a, b, c, x[i + 4], 11, 1272893353)
    c = md5hh(c, d, a, b, x[i + 7], 16, -155497632)
    b = md5hh(b, c, d, a, x[i + 10], 23, -1094730640)
    a = md5hh(a, b, c, d, x[i + 13], 4, 681279174)
    d = md5hh(d, a, b, c, x[i], 11, -358537222)
    c = md5hh(c, d, a, b, x[i + 3], 16, -722521979)
    b = md5hh(b, c, d, a, x[i + 6], 23, 76029189)
    a = md5hh(a, b, c, d, x[i + 9], 4, -640364487)
    d = md5hh(d, a, b, c, x[i + 12], 11, -421815835)
    c = md5hh(c, d, a, b, x[i + 15], 16, 530742520)
    b = md5hh(b, c, d, a, x[i + 2], 23, -995338651)
    a = md5ii(a, b, c, d, x[i], 6, -198630844)
    d = md5ii(d, a, b, c, x[i + 7], 10, 1126891415)
    c = md5ii(c, d, a, b, x[i + 14], 15, -1416354905)
    b = md5ii(b, c, d, a, x[i + 5], 21, -57434055)
    a = md5ii(a, b, c, d, x[i + 12], 6, 1700485571)
    d = md5ii(d, a, b, c, x[i + 3], 10, -1894986606)
    c = md5ii(c, d, a, b, x[i + 10], 15, -1051523)
    b = md5ii(b, c, d, a, x[i + 1], 21, -2054922799)
    a = md5ii(a, b, c, d, x[i + 8], 6, 1873313359)
    d = md5ii(d, a, b, c, x[i + 15], 10, -30611744)
    c = md5ii(c, d, a, b, x[i + 6], 15, -1560198380)
    b = md5ii(b, c, d, a, x[i + 13], 21, 1309151649)
    a = md5ii(a, b, c, d, x[i + 4], 6, -145523070)
    d = md5ii(d, a, b, c, x[i + 11], 10, -1120210379)
    c = md5ii(c, d, a, b, x[i + 2], 15, 718787259)
    b = md5ii(b, c, d, a, x[i + 9], 21, -343485551)
    a = safeAdd(a, oa); b = safeAdd(b, ob); c = safeAdd(c, oc); d = safeAdd(d, od)
  }
  return [a, b, c, d]
}

function str2binl(str) {
  const bin = []
  const mask = (1 << 8) - 1
  for (let i = 0; i < str.length * 8; i += 8) {
    bin[i >> 5] |= (str.charCodeAt(i / 8) & mask) << (i % 32)
  }
  return bin
}

function binl2hex(binarray) {
  const hexTab = '0123456789abcdef'
  let str = ''
  for (let i = 0; i < binarray.length * 4; i++) {
    str += hexTab.charAt((binarray[i >> 2] >> ((i % 4) * 8 + 4)) & 0xf) +
           hexTab.charAt((binarray[i >> 2] >> ((i % 4) * 8)) & 0xf)
  }
  return str
}

export function md5(str) {
  return binl2hex(binlMD5(str2binl(str), str.length * 8))
}

// AES-256-CBC (compact implementation, PKCS7 padding)
const SBOX = [
  0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
  0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
  0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
  0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
  0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
  0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
  0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
  0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
  0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
  0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
  0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
  0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
  0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
  0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
  0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
  0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

function subBytes(s) { for (let i = 0; i < 16; i++) s[i] = SBOX[s[i]] }
function shiftRows(s) {
  let t = s[1]; s[1]=s[5]; s[5]=s[9]; s[9]=s[13]; s[13]=t
  t=s[2]; s[2]=s[10]; s[10]=t; t=s[6]; s[6]=s[14]; s[14]=t
  t=s[15]; s[15]=s[11]; s[11]=s[7]; s[7]=s[3]; s[3]=t
}
function addRoundKey(s, k) { for (let i = 0; i < 16; i++) s[i] ^= k[i] }

const RCON = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36]
function expandKey(key) {
  const w = new Uint8Array(240)
  w.set(key)
  for (let i = 16; i < 240; i += 4) {
    let t = [w[i-4],w[i-3],w[i-2],w[i-1]]
    if (i % 16 === 0) {
      t = [SBOX[t[1]]^RCON[(i/16)-1], SBOX[t[2]], SBOX[t[3]], SBOX[t[0]]]
    }
    for (let j = 0; j < 4; j++) w[i+j] = w[i-16+j] ^ t[j]
  }
  return w
}

function aesEncryptBlock(block, w) {
  const s = new Uint8Array(block)
  addRoundKey(s, w.subarray(0, 16))
  for (let r = 1; r < 14; r++) {
    subBytes(s); shiftRows(s)
    // mixColumns
    for (let c = 0; c < 4; c++) {
      const i = c*4
      const a=[s[i],s[i+1],s[i+2],s[i+3]]
      s[i]   = 0x02*a[0] ^ 0x03*a[1] ^ a[2] ^ a[3]
      s[i+1] = a[0] ^ 0x02*a[1] ^ 0x03*a[2] ^ a[3]
      s[i+2] = a[0] ^ a[1] ^ 0x02*a[2] ^ 0x03*a[3]
      s[i+3] = 0x03*a[0] ^ a[1] ^ a[2] ^ 0x02*a[3]
      // reduce
      for (let k = 0; k < 4; k++) if (s[i+k] & 0x100) s[i+k] ^= 0x11b
    }
    addRoundKey(s, w.subarray(r*16, r*16+16))
  }
  subBytes(s); shiftRows(s); addRoundKey(s, w.subarray(224, 240))
  return s
}

function aesDecryptBlock(block, w) {
  const INV_SBOX = new Uint8Array(256)
  for (let i = 0; i < 256; i++) INV_SBOX[SBOX[i]] = i
  const s = new Uint8Array(block)
  addRoundKey(s, w.subarray(224, 240))
  for (let r = 13; r >= 1; r--) {
    // invShiftRows
    let t=s[13]; s[13]=s[9]; s[9]=s[5]; s[5]=s[1]; s[1]=t
    t=s[10]; s[10]=s[2]; s[2]=t; t=s[14]; s[14]=s[6]; s[6]=t
    t=s[3]; s[3]=s[7]; s[7]=s[11]; s[11]=s[15]; s[15]=t
    for (let i = 0; i < 16; i++) s[i] = INV_SBOX[s[i]]
    addRoundKey(s, w.subarray(r*16, r*16+16))
    // invMixColumns
    for (let c = 0; c < 4; c++) {
      const i = c*4
      const a=[s[i],s[i+1],s[i+2],s[i+3]]
      s[i]   = 0x0e*a[0]^0x0b*a[1]^0x0d*a[2]^0x09*a[3]
      s[i+1] = 0x09*a[0]^0x0e*a[1]^0x0b*a[2]^0x0d*a[3]
      s[i+2] = 0x0d*a[0]^0x09*a[1]^0x0e*a[2]^0x0b*a[3]
      s[i+3] = 0x0b*a[0]^0x0d*a[1]^0x09*a[2]^0x0e*a[3]
      for (let k = 0; k < 4; k++) {
        let v = s[i+k]
        if (v & 0x100) v ^= 0x11b; if (v & 0x200) v ^= 0x211b
        s[i+k] = v
      }
    }
  }
  for (let i = 0; i < 16; i++) s[i] = INV_SBOX[s[i]]
  // invShiftRows
  let t=s[13]; s[13]=s[9]; s[9]=s[5]; s[5]=s[1]; s[1]=t
  t=s[10]; s[10]=s[2]; s[2]=t; t=s[14]; s[14]=s[6]; s[6]=t
  t=s[3]; s[3]=s[7]; s[7]=s[11]; s[11]=s[15]; s[15]=t
  addRoundKey(s, w.subarray(0, 16))
  return s
}

function pkcs7Pad(data) {
  const pad = 16 - (data.length % 16)
  const out = new Uint8Array(data.length + pad)
  out.set(data)
  for (let i = data.length; i < out.length; i++) out[i] = pad
  return out
}

function pkcs7Unpad(data) {
  const pad = data[data.length - 1]
  return data.subarray(0, data.length - pad)
}

function strToBytes(str) {
  const bytes = new Uint8Array(str.length)
  for (let i = 0; i < str.length; i++) bytes[i] = str.charCodeAt(i)
  return bytes
}

function bytesToBase64(bytes) {
  let binary = ''
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
  return btoa(binary)
}

function base64ToBytes(b64) {
  const binary = atob(b64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  return bytes
}

function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) bytes[i / 2] = parseInt(hex.substr(i, 2), 16)
  return bytes
}

const AES_KEY = hexToBytes('a71d42042d0e66063fae9358fd4cdfd665a257e529e5549691cc5dc076fd9daf')
const AES_IV = hexToBytes('01498940ea40890cad568fce8ae04763')
const expandedKey = expandKey(AES_KEY)

export function aesEncrypt(plaintext) {
  const data = strToBytes(plaintext)
  const padded = pkcs7Pad(data)
  const encrypted = new Uint8Array(padded.length)
  for (let i = 0; i < padded.length; i += 16) {
    const block = padded.subarray(i, i + 16)
    // XOR with IV (first block) or previous ciphertext (CBC)
    const xored = new Uint8Array(16)
    const iv = i === 0 ? AES_IV : encrypted.subarray(i - 16, i)
    for (let j = 0; j < 16; j++) xored[j] = block[j] ^ iv[j]
    encrypted.set(aesEncryptBlock(xored, expandedKey), i)
  }
  return bytesToBase64(encrypted)
}

export function aesDecrypt(ciphertext) {
  const data = base64ToBytes(ciphertext)
  const decrypted = new Uint8Array(data.length)
  for (let i = 0; i < data.length; i += 16) {
    const block = data.subarray(i, i + 16)
    const dec = aesDecryptBlock(block, expandedKey)
    const iv = i === 0 ? AES_IV : data.subarray(i - 16, i)
    for (let j = 0; j < 16; j++) decrypted[i + j] = dec[j] ^ iv[j]
  }
  return String.fromCharCode(...pkcs7Unpad(decrypted))
}
