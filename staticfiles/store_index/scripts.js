            $(function() {
                $("#submit").click(function() {
                    html2canvas($("#section_to_capture")[0]).then((canvas) => {
                        
                        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                        function b64toBlob(b64Data, contentType, sliceSize) {
                            contentType = contentType || '';
                            sliceSize = sliceSize || 512;
    
                            var byteCharacters = atob(b64Data);
                            var byteArrays = [];
    
                            for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
                                var slice = byteCharacters.slice(offset, offset + sliceSize);
                                var byteNumbers = new Array(slice.length);
                                for (var i = 0; i < slice.length; i++) {
                                    byteNumbers[i] = slice.charCodeAt(i);
                                }
                                var byteArray = new Uint8Array(byteNumbers);
                                byteArrays.push(byteArray);
                            }
    
                        var blob = new Blob(byteArrays, {type: contentType});
                        return blob;
                    }
    
                    image_data = canvas.toDataURL('image/png'); //use can use image/jpg to generate JPG format image
                    var block = image_data.split(";");
                    var contentType = block[0].split(":")[1]
                    var realData = block[1].split(",")[1];
    
                    var blob = b64toBlob(realData, contentType);
                    var formData = new FormData();
                    formData.append("screenshot", blob, 'screenshot.png');
    
                    $.ajax({
                            url: "/api/save_screenshot",
                            type: "POST",
                            headers: {'X-CSRFToken': csrftoken},
                            mode: 'same-origin',
                            timeout: 0,
                            processData: false,
                            mimeType: "multipart/form-data",
                            contentType: false,
                            data: formData,
                            dataType:"json",
                            success: function (data) {
                                alert("Screenshot saved successfully!");
                            },
                            error: function (e) {
                                console.log(e);
                            }
                            }).done(function(o) {
    
                        });
                        
                    });
                });
            });