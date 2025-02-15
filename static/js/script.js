let uploadedImages = 0;
        const maxImages = 5;
        const uploadBtn = document.getElementById('uploadBtn');
        const imageUpload = document.getElementById('imageUpload');
        const imageContainer = document.getElementById('imageContainer');

        uploadBtn.addEventListener('click', () => {
            if (uploadedImages < maxImages) {
                imageUpload.click();
            } else {
                alert("You can only upload up to 5 images.");
            }
        });

        imageUpload.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file && uploadedImages < maxImages) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement("img");
                    img.src = e.target.result;
                    imageContainer.appendChild(img);
                    uploadedImages++;

                    if (uploadedImages >= maxImages) {
                        uploadBtn.disabled = true;
                        uploadBtn.style.backgroundColor = "gray";
                        uploadBtn.innerText = "Limit Reached";
                    }
                };
                reader.readAsDataURL(file);
            }
        });