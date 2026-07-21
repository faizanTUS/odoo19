/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";
import ajax from "web.ajax";

const SELECTORS = {
    timer: '#otpTimer',
    timerContainer: '#otpTimerContainer',
    resendContainer: '#otpResendContainer',
    resendBtn: '#otpResendBtn',
    messageContainer: '#otpMessage',

    verifyBtnContainer: '#verifyBtnContainer',
    resendBtnInvalidContainer: '#resendBtnInvalidContainer',
    resendBtnInvalid: '#otpResendBtnInvalid',
};

let timerInterval;
let TIMER_DURATION = 2; // 2 minutes in seconds

$(document).ready(function () {
    const timerDisplay = document.querySelector(SELECTORS.timer);
    if (timerDisplay) {
        const expiryTime = parseInt(document.getElementById('expiry_time').value) * 60 || 120;
        startOtpTimer(expiryTime, timerDisplay);
    }

    $(SELECTORS.resendBtn).on('click', function (e) {
        e.preventDefault();
        handleOtpResend();
    });

    // Handle invalid OTP resend button
    $(SELECTORS.resendBtnInvalid).on('click', function (e) {
        e.preventDefault();
        handleOtpResend();
    });

    // Cleanup on page unload
    $(window).on('unload', function () {
        if (timerInterval) {
            clearInterval(timerInterval);
        }
    });
});

// function handleOtpResend() {
//     setOtpFormReadOnly(true);
//
//     const login = document.getElementById('login').value;
//     const name = document.getElementById('name')?.value;
//     const password = document.getElementById('password')?.value;
//     const confirmPassword = document.getElementById('confirm_password')?.value;
//
//     const endpoint = name ? '/web/signup/otp/resend' : '/web/otp/resend';
//     const params = { login };
//     if (name) {
//         params.name = name;
//         params.password = password;
//         params.confirm_password = confirmPassword;
//     }
//
//     jsonrpc(endpoint, params).then(function (result) {
//         if (result.resend_otp) {
//             showOtpMessage('OTP has been resent to your email. Please check your inbox.', 'success');
//             const newExpiryTime = parseInt(document.getElementById('expiry_time').value) * 60 || 120;
//             startOtpTimer(newExpiryTime, document.querySelector(SELECTORS.timer));
//
//             $('#otpErrorMsg').hide();
//             $(SELECTORS.verifyBtnContainer).show();
//             $(SELECTORS.resendBtnInvalidContainer).hide();
//
//         } else if (result.error) {
//             showOtpMessage(result.error, 'danger');
//         }
//     }).finally(() => {
//         setOtpFormReadOnly(false);
//     });
// }

function handleOtpResend() {
    setOtpFormReadOnly(true);

    const login = document.getElementById('login').value;
    const name = document.getElementById('name')?.value;
    const password = document.getElementById('password')?.value;
    const confirmPassword = document.getElementById('confirm_password')?.value;

    const endpoint = name ? '/web/signup/otp/resend' : '/web/otp/resend';

    const params = { login };
    if (name) {
        params.name = name;
        params.password = password;
        params.confirm_password = confirmPassword;
    }

    ajax.jsonRpc(endpoint, 'call', params)
        .then(function (result) {
            if (result.resend_otp) {
                showOtpMessage(
                    'OTP has been resent to your email. Please check your inbox.',
                    'success'
                );

                const newExpiryTime =
                    parseInt(document.getElementById('expiry_time').value) * 60 || 120;

                startOtpTimer(newExpiryTime, document.querySelector(SELECTORS.timer));

                $('#otpErrorMsg').hide();
                $(SELECTORS.verifyBtnContainer).show();
                $(SELECTORS.resendBtnInvalidContainer).hide();
            } else if (result.error) {
                showOtpMessage(result.error, 'danger');
            }
        })
        .finally(() => {
            setOtpFormReadOnly(false);
        });
}



function startOtpTimer(duration, display) {
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    $(SELECTORS.timerContainer).show();
    $(SELECTORS.resendContainer).hide();

    let timer = duration;
    timerInterval = setInterval(function () {
        const minutes = Math.floor(timer / 60);
        const seconds = timer % 60;
        display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        if (--timer < 0) {
            clearInterval(timerInterval);
            $(SELECTORS.timerContainer).hide();
            $(SELECTORS.resendContainer).show();
        }
    }, 1000);
}

function setOtpFormReadOnly(readonly) {
    $('#otp, button[type="submit"], #otpResendBtn, #otpResendBtnInvalid').prop('disabled', readonly);

}

function showOtpMessage(message, type) {
    const messageEl = $(SELECTORS.messageContainer);
    messageEl.removeClass('alert-success alert-danger')
             .addClass(`alert-${type}`)
             .text(message)
             .show();
}
