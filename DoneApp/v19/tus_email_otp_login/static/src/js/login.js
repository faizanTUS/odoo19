/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";

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

// Use native JavaScript instead of jQuery document.ready
function initializeOtpTimer() {
    const timerDisplay = document.querySelector(SELECTORS.timer);
    if (timerDisplay) {
        const expiryTime = parseInt(document.getElementById('expiry_time').value) * 60 || 120;
        startOtpTimer(expiryTime, timerDisplay);
    }

    // Add event listeners using vanilla JavaScript
    const resendBtn = document.querySelector(SELECTORS.resendBtn);
    if (resendBtn) {
        resendBtn.addEventListener('click', function (e) {
            e.preventDefault();
            handleOtpResend();
        });
    }

    const resendBtnInvalid = document.querySelector(SELECTORS.resendBtnInvalid);
    if (resendBtnInvalid) {
        resendBtnInvalid.addEventListener('click', function (e) {
            e.preventDefault();
            handleOtpResend();
        });
    }

    // Cleanup on page unload
    window.addEventListener('unload', function () {
        if (timerInterval) {
            clearInterval(timerInterval);
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeOtpTimer);
} else {
    initializeOtpTimer();
}

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

    rpc(endpoint, params).then(function (result) {
        if (result.resend_otp) {
            showOtpMessage('OTP has been resent to your email. Please check your inbox.', 'success');
            const newExpiryTime = parseInt(document.getElementById('expiry_time').value) * 60 || 120;
            startOtpTimer(newExpiryTime, document.querySelector(SELECTORS.timer));

            const errorMsg = document.getElementById('otpErrorMsg');
            if (errorMsg) errorMsg.style.display = 'none';

            const verifyContainer = document.querySelector(SELECTORS.verifyBtnContainer);
            if (verifyContainer) verifyContainer.style.display = 'block';

            const resendInvalidContainer = document.querySelector(SELECTORS.resendBtnInvalidContainer);
            if (resendInvalidContainer) resendInvalidContainer.style.display = 'none';

        } else if (result.error) {
            showOtpMessage(result.error, 'danger');
        }
    }).finally(() => {
        setOtpFormReadOnly(false);
    });
}

function startOtpTimer(duration, display) {
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    const timerContainer = document.querySelector(SELECTORS.timerContainer);
    const resendContainer = document.querySelector(SELECTORS.resendContainer);

    if (timerContainer) timerContainer.style.display = 'block';
    if (resendContainer) resendContainer.style.display = 'none';

    let timer = duration;
    timerInterval = setInterval(function () {
        const minutes = Math.floor(timer / 60);
        const seconds = timer % 60;
        display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        if (--timer < 0) {
            clearInterval(timerInterval);
            if (timerContainer) timerContainer.style.display = 'none';
            if (resendContainer) resendContainer.style.display = 'block';
        }
    }, 1000);
}

function setOtpFormReadOnly(readonly) {
    const elements = document.querySelectorAll('#otp, button[type="submit"], #otpResendBtn, #otpResendBtnInvalid');
    elements.forEach(el => {
        el.disabled = readonly;
    });
}

function showOtpMessage(message, type) {
    const messageEl = document.querySelector(SELECTORS.messageContainer);
    if (messageEl) {
        messageEl.classList.remove('alert-success', 'alert-danger');
        messageEl.classList.add(`alert-${type}`);
        messageEl.textContent = message;
        messageEl.style.display = 'block';
    }
}