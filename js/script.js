document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const uploadArea = document.getElementById("upload-area")
  const uploadContent = document.getElementById("upload-content")
  const fileInput = document.getElementById("file-upload")
  const previewImage = document.getElementById("preview-image")
  const loadingIndicator = document.getElementById("loading-indicator")
  const editorSection = document.getElementById("editor-section")
  const processedImage = document.getElementById("processed-image")
  const colorButtons = document.querySelectorAll(".color-btn")
  const resetBtn = document.getElementById("reset-btn")
  const downloadBtn = document.getElementById("download-btn")

  let originalImage = null
  let currentColor = "blue" // Default color

  // Event Listeners
  uploadArea.addEventListener("click", () => {
    fileInput.click()
  })

  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault()
    uploadArea.classList.add("active")
  })

  uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("active")
  })

  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault()
    uploadArea.classList.remove("active")

    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files
      handleFileUpload()
    }
  })

  fileInput.addEventListener("change", handleFileUpload)

  colorButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const color = this.getAttribute("data-color")
      changeBackgroundColor(color)

      // Update active state
      colorButtons.forEach((btn) => btn.classList.remove("active"))
      this.classList.add("active")
    })
  })

  resetBtn.addEventListener("click", () => {
    // Reset to upload state
    editorSection.classList.add("hidden")
    uploadContent.classList.remove("hidden")
    previewImage.classList.add("hidden")
    fileInput.value = ""
  })

  downloadBtn.addEventListener("click", downloadImage)

  // Functions
  function handleFileUpload() {
    if (fileInput.files && fileInput.files[0]) {
      const file = fileInput.files[0]

      // Check if file is an image
      if (!file.type.match("image.*")) {
        alert("Please upload an image file")
        return
      }

      // Show preview
      const reader = new FileReader()
      reader.onload = (e) => {
        previewImage.src = e.target.result
        previewImage.classList.remove("hidden")
        uploadContent.classList.add("hidden")

        // Show loading indicator
        uploadArea.classList.add("hidden")
        loadingIndicator.classList.remove("hidden")

        // Send image to server for processing
        processImage(file)
      }
      reader.readAsDataURL(file)
    }
  }

  function processImage(file) {
    const formData = new FormData()
    formData.append("image", file)

    fetch("/process-image", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok")
        }
        return response.json()
      })
      .then((data) => {
        // Hide loading indicator
        loadingIndicator.classList.add("hidden")

        // Show editor section
        editorSection.classList.remove("hidden")

        // Set processed image
        processedImage.src = data.image_url
        originalImage = data.image_url

        // Set default background color
        changeBackgroundColor("blue")
        document.querySelector('[data-color="blue"]').classList.add("active")
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("There was an error processing your image. Please try again.")

        // Reset UI
        loadingIndicator.classList.add("hidden")
        uploadArea.classList.remove("hidden")
        uploadContent.classList.remove("hidden")
        previewImage.classList.add("hidden")
      })
  }

  function changeBackgroundColor(color) {
    currentColor = color

    // Send request to change background color
    fetch("/change-background", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image_url: originalImage,
        color: color,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        processedImage.src = data.image_url + "?t=" + new Date().getTime() // Add timestamp to prevent caching
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("There was an error changing the background color.")
      })
  }

  function downloadImage() {
    // Create a link element
    const link = document.createElement("a")
    link.href = processedImage.src
    link.download = "passport_photo_" + currentColor + ".png"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
})
