odoo.define('tus_screenshort_by_attendence.my_attendances_ss', function(require) {
  "use strict";

  var AbstractActionSS = require('hr_attendance.my_attendances');
  var core = require('web.core');
  var rpc = require('web.rpc')

// include hr_attendance inside AbstractAction wizard
  var MyAttendances = AbstractActionSS.include({
    init: function(parent, action) {
        var self = this;
        this._super.apply(this, arguments);
    },
    // Form load time constrains and video added and also check mediaDevices library and getUserMedia accessible worked or not and also checked video permission accessible or not.
    start: function() {
      var self = this;
      window.error_tag = document.querySelector('h6');
      var constraints = {
        video: true
      };
      // "navigator.mediaDevices.getUserMedia(constraints)" this library function used to video streaming started.
      navigator.mediaDevices.getUserMedia(constraints)
      .then(function(mediaStream) {
        try {
          video.pause();
          video.srcObject.getTracks().forEach(function(track) { track.stop(); })
          window.video = document.querySelector('video');
          window.video.style.visibility='visible';

        } catch(e) {
          window.video = document.querySelector('video');
          window.video.style.visibility='visible';
        }
        window.video.srcObject = mediaStream;
        window.video.play();
      })
      .catch(function (e) {
        // when all browser or streaming method worked or not on device.

        window.error_tag = document.querySelector('h6');
        window.error_tag.innerHTML=e;
      });
      return this._super.apply(this, arguments);
    },
    // When another form view open thne attendance check in check out scope is eneded this time streaming distroyed.
    destroy: function () {
        this._super.apply(this, arguments);
        if (window.video){
          video.srcObject.getTracks().forEach(function(track) { track.stop(); })
          window.video.pause();
          delete window.canvas;
        }
    },
//  Base function overight
    update_attendance: function() {
      var self = this;
      this._rpc({
          model: 'hr.employee',
          method: 'attendance_manual',
          args: [
            [self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'
          ],
        })
        .then(function(result) {
          if (result.action) {
            try{
              var rec = self.captureVideoButton(video);
              self.do_action(result.action);
              rpc.query({
                    model: 'hr.attendance',
                    method: 'get_image_check_in_out',
                    args: [[result.action.attendance.id], {'check_out_time': result.action,'attendance_id': result.action.attendance.id, 'check_in_out_image': rec.src}],
                }).then(function (returned_value){
                  video.pause();
                  video.srcObject.getTracks().forEach(function(track) { track.stop(); })
                  delete window.canvas;
                })
            }catch{
              self.do_action(result.action);
            }
          } else if (result.warning) {
            self.do_warn(result.warning);
          }
        });
    },
// method called load to video and capture the img on video streaming and after that video streaming ended.
    captureVideoButton : function(video) {
      var self = this;
      var captureVideoimage = this.onloadedmetadata(video);
      return captureVideoimage
    },
    onloadedmetadata : function(video) {
      var img = document.querySelector('#screenshot img');
      window.canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      img.src = canvas.toDataURL('image/webp');
      video.pause();
      return img
    },

  });
  return MyAttendances
});
