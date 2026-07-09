/**@odoo-module **/

import {ActivityMenu} from "@hr_attendance/components/attendance_menu/attendance_menu";
import {patch} from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";

patch(ActivityMenu.prototype, {
    stateChanged(state) {
        if (state) {
            window.error_tag = document.querySelector('h6');
            var constraints = {
                video: true
            };
            // "navigator.mediaDevices.getUserMedia(constraints)" this library function used to video streaming started.
            navigator.mediaDevices.getUserMedia(constraints).then(function (mediaStream) {
                window.video = document.querySelector('video');
                if (window.video) {
                    window.video = document.querySelector('video');
                    try {
                        window.video.pause();
                        //              window.video.srcObject.getTracks().forEach(function(track) { track.stop(); })
                        window.video.style.visibility = 'visible';
                    } catch (e) {
                        window.video = document.querySelector('video');
                        window.video.style.visibility = 'visible';
                    }
                    window.video.srcObject = mediaStream;
                    window.video.play();
                }
            });
        } else if (!state.open) {
            window.video.srcObject.getTracks().forEach((track) => {
                if (track.readyState == 'live' && track.kind === 'video') {
                    track.stop();
                }
            });
        }
    },

    async signInOut() {
        var rec = this.captureVideoButton();
        navigator.geolocation.getCurrentPosition(
            async ({coords: {latitude, longitude, check_in_out_image}}) => {
                await rpc("/hr_attendance/systray_check_in_out", {
                    latitude,
                    longitude,
                    check_in_out_image: rec.src,
                })
                await this.searchReadEmployee()
            },
            async err => {
                await this.rpc("/hr_attendance/systray_check_in_out")
                await this.searchReadEmployee()
            }
        )
    },

    captureVideoButton() {
        var self = this;
        var captureVideoimage = this.onloadedmetadata();
        return captureVideoimage
    },
    onloadedmetadata() {
        var img = document.querySelector('#screenshot img');
        window.canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        img.src = canvas.toDataURL('image/webp');
        video.pause();
        return img
    },
})