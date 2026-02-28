/**
 * Composable: usePhotoCompressor
 * Ports PhotoCompressor class from public/js/photo_compressor.js.
 * Uses Canvas API to resize + compress images before upload.
 */

const MAX_WIDTH = 1024
const MAX_HEIGHT = 1024
const JPEG_QUALITY = 0.8
const OUTPUT_MIME_TYPE = 'image/jpeg'

export function usePhotoCompressor() {
  /**
   * Compress an image File. Returns dataUrl, Blob, and a safe filename.
   * Throws if the file is not an image.
   */
  async function compressFile(file) {
    if (!file.type.startsWith('image/')) {
      throw new Error('Selected file is not an image')
    }

    const originalDataUrl = await readFileAsDataUrl(file)
    const imageElement = await loadImageFromDataUrl(originalDataUrl)
    const compressedDataUrl = renderToCanvas(imageElement)
    const compressedBlob = dataUrlToBlob(compressedDataUrl)
    const compressedFilename = buildFilename(file.name)

    return { dataUrl: compressedDataUrl, blob: compressedBlob, filename: compressedFilename }
  }

  // --- Private helpers ---

  function readFileAsDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (event) => resolve(event.target.result)
      reader.onerror = () => reject(new Error('Failed to read image file'))
      reader.readAsDataURL(file)
    })
  }

  function loadImageFromDataUrl(dataUrl) {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('Failed to decode image'))
      img.src = dataUrl
    })
  }

  function renderToCanvas(imageElement) {
    const { width, height } = scaleDownIfNeeded(imageElement.width, imageElement.height)

    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height

    const ctx = canvas.getContext('2d')
    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = 'high'
    ctx.drawImage(imageElement, 0, 0, width, height)

    return canvas.toDataURL(OUTPUT_MIME_TYPE, JPEG_QUALITY)
  }

  function scaleDownIfNeeded(originalWidth, originalHeight) {
    if (originalWidth <= MAX_WIDTH && originalHeight <= MAX_HEIGHT) {
      return { width: originalWidth, height: originalHeight }
    }
    const scalingRatio = Math.min(MAX_WIDTH / originalWidth, MAX_HEIGHT / originalHeight)
    return {
      width: Math.round(originalWidth * scalingRatio),
      height: Math.round(originalHeight * scalingRatio),
    }
  }

  function dataUrlToBlob(dataUrl) {
    const [header, base64Data] = dataUrl.split(',')
    const mimeType = header.match(/:(.*?);/)[1]
    const binaryString = atob(base64Data)
    const byteArray = new Uint8Array(binaryString.length)
    for (let i = 0; i < binaryString.length; i++) {
      byteArray[i] = binaryString.charCodeAt(i)
    }
    return new Blob([byteArray], { type: mimeType })
  }

  function buildFilename(originalName) {
    const baseName = originalName.replace(/\.[^.]+$/, '')
    return `${baseName}_compressed.jpg`
  }

  return { compressFile }
}
