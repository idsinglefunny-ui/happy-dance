import * as CryptoJS from 'crypto-js'

const AES_KEY = CryptoJS.enc.Hex.parse('a71d42042d0e66063fae9358fd4cdfd665a257e529e5549691cc5dc076fd9daf')
const AES_IV = CryptoJS.enc.Hex.parse('01498940ea40890cad568fce8ae04763')

export function md5(str) {
  return CryptoJS.MD5(str).toString()
}

export function aesEncrypt(plaintext) {
  const encrypted = CryptoJS.AES.encrypt(plaintext, AES_KEY, {
    iv: AES_IV,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  })
  return encrypted.toString()
}

export function aesDecrypt(ciphertext) {
  const decrypted = CryptoJS.AES.decrypt(ciphertext, AES_KEY, {
    iv: AES_IV,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  })
  return decrypted.toString(CryptoJS.enc.Utf8)
}
