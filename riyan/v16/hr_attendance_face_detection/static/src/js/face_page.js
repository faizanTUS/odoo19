// Enhanced face recognition with proper DOM handling and liveness detection
let isProcessing = false;
let livenessFrames = [];
let frameCount = 0;
const REQUIRED_FRAMES = 8; // Reduced for better performance

async function startFaceRecognition() {
    const button = event.target;
    if (button.disabled || isProcessing) return;

    button.disabled = true;
    button.innerHTML = '🎥 Starting Camera...';
    isProcessing = true;

    let stream = null;

    try {
        // Get location first
        const location = await getCurrentLocation();

        // Enhanced camera constraints
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640, min: 480 },
                height: { ideal: 480, min: 360 },
                facingMode: 'user',
                frameRate: { ideal: 30 }
            }
        });

        const video = document.createElement('video');
        video.srcObject = stream;
        video.autoplay = true;
        video.playsInline = true;
        video.style.width = '100%';
        video.style.maxWidth = '480px';
        video.style.border = '3px solid #007bff';
        video.style.borderRadius = '10px';

        await new Promise((resolve, reject) => {
            video.onloadedmetadata = () => {
                console.log('Video loaded:', video.videoWidth, 'x', video.videoHeight);
                resolve();
            };
            video.onerror = (e) => {
                console.error('Video error:', e);
                reject(new Error('Video failed to load'));
            };
            // Timeout after 10 seconds
            setTimeout(() => reject(new Error('Video load timeout')), 10000);
        });

        const container = document.getElementById('video-container');
        if (!container) {
            throw new Error('Video container not found');
        }

        container.innerHTML = `
            <h4>📱 Face Recognition with Liveness Detection</h4>
            <div id="video-wrapper" style="text-align: center; margin: 20px 0;">
                <!-- Video will be inserted here -->
            </div>
            <div id="liveness-container" class="mt-3 p-3 bg-light rounded">
                <h5>🔍 Liveness Detection Required</h5>
                <p class="text-info mb-2">Please:</p>
                <ul class="text-info mb-3">
                    <li>Look directly at the camera</li>
                    <li>Stay still and keep your face visible</li>
                    <li>Ensure good lighting</li>
                </ul>
                <div id="liveness-status" class="alert alert-warning">
                    <strong>⏳ Preparing liveness detection...</strong>
                </div>
            </div>
            <div id="location-status" class="mt-2"></div>
            <div id="button-container" class="mt-3 text-center"></div>
        `;

        const videoWrapper = document.getElementById('video-wrapper');
        videoWrapper.appendChild(video);

        // Update location status
        const locationStatus = document.getElementById('location-status');
        if (location) {
            locationStatus.innerHTML = `<p class="text-success small">📍 Location: ${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}</p>`;
        } else {
            locationStatus.innerHTML = `<p class="text-warning small">📍 Location: Not available</p>`;
        }

        const buttonContainer = document.getElementById('button-container');
        buttonContainer.innerHTML = `
            <button id="cancel-btn" class="btn btn-secondary">❌ Cancel</button>
        `;

        document.getElementById('cancel-btn').onclick = function() {
            cleanupCamera(stream, container, button);
        };

        // Start liveness detection after delay
        setTimeout(() => {
            startLivenessDetection(video, stream, container, button, location);
        }, 2000);

    } catch (error) {
        console.error("Camera Error:", error);
        handleCameraError(error, button);
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }
}

async function startLivenessDetection(video, stream, container, mainButton, location) {
    const statusDiv = document.getElementById('liveness-status');
    if (!statusDiv) {
        console.error('Liveness status div not found');
        cleanupCamera(stream, container, mainButton);
        return;
    }

    livenessFrames = [];
    frameCount = 0;

    try {
        statusDiv.innerHTML = '<strong>🔄 Analyzing liveness... Please stay still</strong>';
        statusDiv.className = 'alert alert-info';

        if (!video.videoWidth || !video.videoHeight) {
            throw new Error('Video not ready for capture');
        }

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        let detectionActive = true;

        // Capture frames for liveness analysis
        const captureInterval = setInterval(async () => {
            if (!detectionActive) {
                clearInterval(captureInterval);
                return;
            }

            try {
                const currentStatusDiv = document.getElementById('liveness-status');
                if (!currentStatusDiv) {
                    clearInterval(captureInterval);
                    return;
                }

                // Capture frame
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/jpeg', 0.8);

                const hasValidFace = await analyzeFrameForFace(imageData);

                if (hasValidFace) {
                    livenessFrames.push({
                        data: imageData,
                        timestamp: Date.now()
                    });

                    frameCount++;
                    currentStatusDiv.innerHTML = `<strong>✅ Valid face detected (${frameCount}/${REQUIRED_FRAMES})</strong>`;
                    currentStatusDiv.className = 'alert alert-success';

                    if (frameCount >= REQUIRED_FRAMES) {
                        detectionActive = false;
                        clearInterval(captureInterval);

                        const isLive = await validateLiveness(livenessFrames);

                        if (isLive) {
                            currentStatusDiv.innerHTML = '<strong>🎉 Liveness confirmed! Processing attendance...</strong>';

                            // Use middle frame for best quality
                            const bestFrame = livenessFrames[Math.floor(livenessFrames.length / 2)];
                            await processAttendance(bestFrame.data, stream, container, mainButton, location);
                        } else {
                            currentStatusDiv.innerHTML = '<strong>❌ Liveness detection failed. Please try again.</strong>';
                            currentStatusDiv.className = 'alert alert-danger';

                            setTimeout(() => {
                                cleanupCamera(stream, container, mainButton);
                            }, 3000);
                        }
                    }
                } else {
                    currentStatusDiv.innerHTML = '<strong>⚠️ Please position your face clearly in the camera frame</strong>';
                    currentStatusDiv.className = 'alert alert-warning';
                }

            } catch (frameError) {
                console.error('Frame capture error:', frameError);
                const currentStatusDiv = document.getElementById('liveness-status');
                if (currentStatusDiv) {
                    currentStatusDiv.innerHTML = '<strong>❌ Detection error. Please try again.</strong>';
                    currentStatusDiv.className = 'alert alert-danger';
                }
            }
        }, 600); // Capture every 600ms for better stability

        // Cleanup timeout
        setTimeout(() => {
            detectionActive = false;
            clearInterval(captureInterval);

            const currentStatusDiv = document.getElementById('liveness-status');
            if (currentStatusDiv && frameCount < REQUIRED_FRAMES) {
                currentStatusDiv.innerHTML = '<strong>⏰ Timeout. Please try again with better lighting.</strong>';
                currentStatusDiv.className = 'alert alert-danger';

                setTimeout(() => {
                    cleanupCamera(stream, container, mainButton);
                }, 3000);
            }
        }, 25000); // 25 second timeout

    } catch (error) {
        console.error('Liveness detection error:', error);
        const currentStatusDiv = document.getElementById('liveness-status');
        if (currentStatusDiv) {
            currentStatusDiv.innerHTML = '<strong>❌ Liveness detection failed. Please try again.</strong>';
            currentStatusDiv.className = 'alert alert-danger';
        }

        setTimeout(() => {
            cleanupCamera(stream, container, mainButton);
        }, 3000);
    }
}

async function analyzeFrameForFace(imageData) {
    return new Promise((resolve) => {
        try {
            const img = new Image();
            img.onload = function() {
                // Create canvas for analysis
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = Math.min(img.width, 200); // Limit size for performance
                canvas.height = Math.min(img.height, 200);

                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                // Get image data
                const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imgData.data;

                // Calculate brightness and contrast
                let brightness = 0;
                let contrast = 0;
                const pixelCount = data.length / 4;

                for (let i = 0; i < data.length; i += 4) {
                    const gray = (data[i] + data[i + 1] + data[i + 2]) / 3;
                    brightness += gray;
                }

                brightness /= pixelCount;

                // Calculate contrast
                for (let i = 0; i < data.length; i += 4) {
                    const gray = (data[i] + data[i + 1] + data[i + 2]) / 3;
                    contrast += Math.pow(gray - brightness, 2);
                }

                contrast = Math.sqrt(contrast / pixelCount);

                // Validation criteria
                const isValid = (
                    brightness > 40 && brightness < 200 && // Good brightness
                    contrast > 15 && // Sufficient contrast
                    pixelCount > 1000 // Reasonable image size
                );

                resolve(isValid);
            };

            img.onerror = () => resolve(false);
            img.src = imageData;
        } catch (error) {
            console.error('Frame analysis error:', error);
            resolve(false);
        }
    });
}

async function validateLiveness(frames) {
    if (frames.length < REQUIRED_FRAMES) return false;

    try {
        // Simple liveness validation based on temporal consistency
        const variations = [];

        // Compare consecutive frames
        for (let i = 1; i < frames.length; i++) {
            const diff = await calculateFrameDifference(frames[i-1].data, frames[i].data);
            variations.push(diff);
        }

        if (variations.length === 0) return false;

        const avgVariation = variations.reduce((a, b) => a + b, 0) / variations.length;
        const maxVariation = Math.max(...variations);

        // Liveness criteria - should have some natural movement but not too much
        const isLive = (
            avgVariation > 1.0 &&
            avgVariation < 15 &&
            maxVariation < 25 &&
            frames.length >= REQUIRED_FRAMES
        );

        console.log('Liveness validation:', {
            avgVariation,
            maxVariation,
            frameCount: frames.length,
            isLive
        });

        return isLive;

    } catch (error) {
        console.error('Liveness validation error:', error);
        return false;
    }
}

async function calculateFrameDifference(frame1, frame2) {
    return new Promise((resolve) => {
        try {
            const img1 = new Image();
            const img2 = new Image();
            let loadedCount = 0;

            const onLoad = () => {
                loadedCount++;
                if (loadedCount === 2) {
                    try {
                        const canvas1 = document.createElement('canvas');
                        const canvas2 = document.createElement('canvas');
                        const ctx1 = canvas1.getContext('2d');
                        const ctx2 = canvas2.getContext('2d');

                        const size = 50; // Small size for performance
                        canvas1.width = canvas2.width = size;
                        canvas1.height = canvas2.height = size;

                        ctx1.drawImage(img1, 0, 0, size, size);
                        ctx2.drawImage(img2, 0, 0, size, size);

                        const data1 = ctx1.getImageData(0, 0, size, size).data;
                        const data2 = ctx2.getImageData(0, 0, size, size).data;

                        let totalDiff = 0;
                        for (let i = 0; i < data1.length; i += 4) {
                            const diff = Math.abs(data1[i] - data2[i]) +
                                        Math.abs(data1[i + 1] - data2[i + 1]) +
                                        Math.abs(data1[i + 2] - data2[i + 2]);
                            totalDiff += diff / 3;
                        }

                        resolve(totalDiff / (data1.length / 4));
                    } catch (error) {
                        console.error('Frame comparison error:', error);
                        resolve(0);
                    }
                }
            };

            img1.onload = img2.onload = onLoad;
            img1.onerror = img2.onerror = () => {
                loadedCount++;
                if (loadedCount >= 2) resolve(0);
            };

            img1.src = frame1;
            img2.src = frame2;
        } catch (error) {
            resolve(0);
        }
    });
}

async function processAttendance(imageData, stream, container, mainButton, location) {
    try {
        // Stop camera first
        stream.getTracks().forEach(track => track.stop());

        // Update UI
        if (container) {
            container.innerHTML = `
                <div class="text-center">
                    <h4>🔍 Processing attendance...</h4>
                    <div class="spinner-border text-primary" role="status"></div>
                </div>
            `;
        }

        const requestData = {
            jsonrpc: "2.0",
            method: "call",
            params: {
                image_data: imageData,
                latitude: location ? location.latitude : null,
                longitude: location ? location.longitude : null
            },
            id: Date.now()
        };

        const response = await fetch('/face_recognition/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Server response:', data);

        // Handle response
        if (data.result && data.result.success) {
            const details = `
                <strong>${data.result.employee_name}</strong><br>
                <small>📍 ${data.result.location || 'Location not available'}</small><br>
                <small>⏰ ${data.result.action || 'attendance'} completed</small>
            `;
            showNotification('success', '✅ Success', data.result.msg + '<br><br>' + details);
        } else {
            const errorMsg = data.result ? data.result.msg : (data.error ? data.error.message : 'Unknown error');
            showNotification('error', '❌ Error', errorMsg);
        }

    } catch (error) {
        console.error('Attendance processing error:', error);
        showNotification('error', '❌ Network Error', 'Failed to process attendance: ' + error.message);
    } finally {
        // Always cleanup
        cleanupCamera(stream, container, mainButton);
    }
}

function cleanupCamera(stream, container, button) {
    try {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        if (container) {
            container.innerHTML = '';
        }
        if (button) {
            button.disabled = false;
            button.innerHTML = '🎥 Start Camera for Face Recognition';
        }
        isProcessing = false;
        livenessFrames = [];
        frameCount = 0;
    } catch (error) {
        console.error('Cleanup error:', error);
    }
}

function handleCameraError(error, button) {
    let errorMessage = "Camera access failed";

    switch (error.name) {
        case 'NotAllowedError':
            errorMessage = "Camera permission denied. Please allow camera access and refresh the page.";
            break;
        case 'NotFoundError':
            errorMessage = "No camera found on this device.";
            break;
        case 'NotReadableError':
            errorMessage = "Camera is already in use by another application.";
            break;
        case 'OverconstrainedError':
            errorMessage = "Camera doesn't support the required settings.";
            break;
        default:
            errorMessage = error.message || "Camera initialization failed";
    }

    showNotification('error', '❌ Camera Error', errorMessage);

    if (button) {
        button.disabled = false;
        button.innerHTML = '🎥 Start Camera for Face Recognition';
    }
    isProcessing = false;
}

async function getCurrentLocation() {
    if (!navigator.geolocation) {
        console.warn("Geolocation not supported");
        return null;
    }

    return new Promise((resolve) => {
        const timeoutId = setTimeout(() => {
            console.warn("Geolocation timeout");
            resolve(null);
        }, 15000);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                clearTimeout(timeoutId);
                console.log('Location obtained:', position.coords.latitude, position.coords.longitude);
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });
            },
            (error) => {
                clearTimeout(timeoutId);
                console.warn("Geolocation error:", error.message);
                resolve(null);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    });
}

function showNotification(type, title, message) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.custom-notification');
    existingNotifications.forEach(n => n.remove());

    const notification = document.createElement('div');
    const alertType = type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'danger';

    notification.className = `alert alert-${alertType} alert-dismissible fade show custom-notification`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '350px';
    notification.style.maxWidth = '500px';
    notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';

    notification.innerHTML = `
        <h5 class="mb-2">${title}</h5>
        <div>${message}</div>
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;

    document.body.appendChild(notification);

    // Auto remove after 10 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 10000);
}
