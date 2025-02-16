let uploadedFiles = [];
    const maxImages = 5;
    
    const uploadBtn = document.getElementById('uploadBtn');
    const imageUpload = document.getElementById('imageUpload');
    const imageContainer = document.getElementById('imageContainer');
    const generateBtn = document.getElementById('generateBtn');
    const additionalPromptEl = document.getElementById('additionalPrompt');
    const generatedImgContainer = document.getElementById('generatedImg');

    // Upload button click triggers file selection
    uploadBtn.addEventListener('click', () => {
      if (uploadedFiles.length < maxImages) {
        imageUpload.click();
      } else {
        alert("You can only upload up to 5 images.");
      }
    });

    // When a file is selected, store it and preview it
    imageUpload.addEventListener('change', function(event) {
      const file = event.target.files[0];
      if (file && uploadedFiles.length < maxImages) {
        uploadedFiles.push(file);  // Store the file
        const reader = new FileReader();
        reader.onload = function(e) {
          const img = document.createElement("img");
          img.src = e.target.result;
          imageContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
        if (uploadedFiles.length >= maxImages) {
          uploadBtn.disabled = true;
          uploadBtn.style.backgroundColor = "gray";
          uploadBtn.innerText = "Limit Reached";
        }
      }
    });

    // When Generate button is clicked, send the files and prompt to the server
    generateBtn.addEventListener('click', async () => {
      if (uploadedFiles.length === 0) {
        alert("Please upload at least one image.");
        return;
      }
      // Create a FormData object and append all image files
      const formData = new FormData();
      uploadedFiles.forEach(file => formData.append("images", file));
      // Append additional prompt text
      formData.append("additional_prompt", additionalPromptEl.value);
      
      try {
        // Replace 'YOUR_NGROK_URL' with your actual ngrok URL if needed.
        const response = await fetch("/generate", {
          method: "POST",
          body: formData
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          alert("Error: " + errorData.error);
          return;
        }
        // Get the returned image blob and display it
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        generatedImgContainer.innerHTML = `<img src="${imageUrl}" alt="Generated Image">`;
      } catch (error) {
        alert("An error occurred: " + error);
      }
    });