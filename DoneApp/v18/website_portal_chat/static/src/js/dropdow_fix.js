/** @odoo-module **/

//console.log("🔧 Dropdown patch loaded safely for Odoo 18 frontend...");

// Bootstrap dropdown global patch
(function () {
    const Dropdown = $.fn.dropdown.Constructor;

    if (Dropdown && Dropdown.prototype) {
        const originalIsShown = Dropdown.prototype._isShown;

        Dropdown.prototype._isShown = function () {
            const target = this._element || this._menu || null;

            if (!target || !target.classList) {
//                console.warn("⚠️ Dropdown._isShown prevented null target");
                return false;
            }
            try {
                return originalIsShown ? originalIsShown.apply(this, arguments) : true;
            } catch (err) {
//                console.warn("⚠️ Dropdown._isShown error handled:", err);
                return false;
            }
        };

//        console.log("✅ Bootstrap Dropdown._isShown patched safely");
    } else {
//        console.warn("❌ No Bootstrap Dropdown found to patch");
    }

    // Close dropdown on scroll event
    $(window).on('scroll', function () {
//        console.log("Scroll detected - closing dropdown");
        $('.dropdown-menu').addClass('d-none');

//        // Check if any dropdown is open and close it
//        $('.dropdown.open').each(function () {
//            const dropdown = $(this);
//            console.log("Closing dropdown: ", dropdown);
//
//            // Ensure dropdown is closed by manually hiding the menu
//            dropdown.removeClass('open');
//            dropdown.find('.dropdown-menu').fadeOut('fast');
//        });
    });


    // Close dropdown when clicking outside (for mobile)
//    $(document).on('click', function (event) {
//        if (!$(event.target).closest('.dropdown').length) {
//            // Close dropdown if clicked outside
//            console.log("Click detected outside - closing dropdown");
//            $('.dropdown.open').removeClass('open');
//            $('.dropdown-menu').fadeOut('fast');
//        }
//    });
})();
