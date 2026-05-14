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

function decryptResponse(res) {
  if (res.data && res.data.data && typeof res.data.data === 'string') {
    try {
      const plain = aesDecrypt(res.data.data)
      if (plain) {
        return { data: JSON.parse(plain), statusCode: res.statusCode }
      }
    } catch (e) {
      console.error('[request] decrypt failed:', e)
    }
  }
  return res
}

export function request(options) {
  const { url, method = 'GET', data = {}, success, fail } = options

  const t = String(Math.floor(Date.now() / 1000))
  const nonce = randomNonce()

  const signedParams = { ...data, t, nonce }
  signedParams.sign = makeSign(signedParams)

  if (method === 'GET') {
    uni.request({
      url: `${BASE_URL}${url}`,
      method: 'GET',
      data: signedParams,
      success: (res) => {
        success && success(decryptResponse(res))
      },
      fail
    })
  } else {
    const encryptedBody = aesEncrypt(JSON.stringify(data))
    uni.request({
      url: `${BASE_URL}${url}?t=${t}&nonce=${nonce}&sign=${signedParams.sign}`,
      method: 'POST',
      data: { _encrypted: encryptedBody },
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        success && success(decryptResponse(res))
      },
      fail
    })
  }
}
