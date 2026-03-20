/** @odoo-module **/
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component } from "@odoo/owl";
import { Notification } from "@web/core/notifications/notification_service";

export class FaceAttendanceButton extends Component {
    static template = "face_attendance.FaceAttendanceTemplate";

    async onCheckInOut() {
        try {
            console.log("▶️ Face Attendance Button clicked");

            // Capture Image
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.createElement("video");
            video.srcObject = stream;
            await video.play();

            const canvas = document.createElement("canvas");
            canvas.width = 320;
            canvas.height = 240;
            canvas.getContext("2d").drawImage(video, 0, 0, 320, 240);
            const image_data = canvas.toDataURL("image/jpeg");

            // Stop camera
            stream.getTracks().forEach((track) => track.stop());
            console.log("📸 Image captured");

            // Get GPS Location
            const location = await this.getCurrentLocation();
            const latitude = location ? location.latitude : null;
            const longitude = location ? location.longitude : null;
            console.log("📤 Sending data to Odoo:", {
                hasImage: !!image_data,
                latitude,
                longitude
            });

            // Call Odoo backend
            const res = await rpc("/face_recognition/check", {
                image_data,
                latitude,
                longitude
            });
            console.log("✅ Odoo Response:", res);

            // 🎯 Show nice snackbar instead of alert
            if (res.success) {
                const details = `
                    👤 ${res.employee_name}
                    \n📍 ${res.location}
                `;
                this.env.services.notification.add(details, { type: "success" });
            } else {
                this.env.services.notification.add(res.msg, { type: "danger" });
            }


        } catch (error) {
            console.error("🔥 Error in Face Attendance:", error);
            this.env.services.notification.add("Error: " + error.message, {
                type: "danger",
            });
        }
    }

    // Geolocation helper
    async getCurrentLocation() {
        if (!navigator.geolocation) {
            console.warn("❌ Geolocation not supported in this browser");
            return null;
        }

        try {
            console.log("📍 Requesting location...");
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        console.log("✅ Location success:", pos.coords.latitude, pos.coords.longitude);
                        resolve(pos);
                    },
                    (err) => {
                        console.warn("⚠️ Location error:", err.message);
                        resolve(null);
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 60000,
                    }
                );
            });
            return position ? position.coords : null;
        } catch (error) {
            console.warn("⚠️ Geolocation failed:", error);
            return null;
        }
    }
}

registry.category("actions").add("face_attendance.button", FaceAttendanceButton);
