$(function() {
    let lastScrollTop = 0;
    const $navTopRow = $("#nav-top-row");
    const threshold = 100; // pixels before triggering hide

    $(window).on("scroll", function() {
      let scrollTop = $(this).scrollTop();

      if (scrollTop > lastScrollTop && scrollTop > threshold) {
        // scrolling down past threshold → animate hide
        if ($navTopRow.is(":visible")) {
          $navTopRow.slideUp(300, function() {
            $navTopRow.addClass("d-none");
          });
        }
      } else if (scrollTop < lastScrollTop) {
        // scrolling up → animate show
        if ($navTopRow.hasClass("d-none")) {
          $navTopRow.removeClass("d-none").hide().slideDown(300);
        }
      }

      lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // avoid negative values
    });
  });
