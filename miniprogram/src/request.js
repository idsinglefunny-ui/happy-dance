import BASE_URL from '@/config.js'
import { md5, aesEncrypt, aesDecrypt } from '@/crypto.js'

const SECRET_KEY = 'dance_king_2026_secret_key'

function makeSign(params) {
  const keys = Object.keys(params).sort()
  let raw = ''
  for (const k of keys) {
    raw += `${k}=${params[k]}&`
  }
  raw += `key=${SECRET_KEY}`
  return md5(raw)
}

function randomNonce() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
  let s = ''
  for (let i = 0; i < 6; i++) s += chars.charAt(Math.floor(Math.random() * chars.length))
  return s
}

export function request(options) {
  const { url, method = 'GET', data = {}, success, fail } = options

  const t = String(Math.floor(Date.now() / 1000))
  const nonce = randomNonce()

  // Merge security params
  const signedParams = { ...data, t, nonce }
  signedParams.sign = makeSign(signedParams)

  if (method === 'GET') {
    uni.request({
      url: `${BASE_URL}${url}`,
      method: 'GET',
      data: signedParams,
      success: (res) => {
        if (res.data && res.data.data) {
          try {
            const decrypted = JSON.parse(aesDecrypt(res.data.data))
            success && success({ data: decrypted, statusCode: res.statusCode })
          } catch (e) {
            success && success(res)
          }
        } else {
          success && success(res)
        }
      },
      fail
    })
  } else {
    // POST: encrypt body, sign goes in query params
    const encryptedBody = aesEncrypt(JSON.stringify(data))
    uni.request({
      url: `${BASE_URL}${url}?t=${t}&nonce=${nonce}&sign=${signedParams.sign}`,
      method: 'POST',
      data: { _encrypted: encryptedBody },
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        if (res.data && res.data.data) {
          try {
            const decrypted = JSON.parse(aesDecrypt(res.data.data))
            success && success({ data: decrypted, statusCode: res.statusCode })
          } catch (e) {
            success && success(res)
          }
        } else {
          success && success(res)
        }
      },
      fail
    })
  }
}
