$(function() {
  let lastScrollTop = 0;
  const $navTopRow = $("#nav-top-row");
  const threshold = 100; // pixels before triggering hide
  let isHidden = false;

  $(window).on("scroll", function() {
    let scrollTop = $(this).scrollTop();

    if (scrollTop > lastScrollTop && scrollTop > threshold) {
      // scrolling down past threshold → hide
      if (!isHidden) {
        $navTopRow.stop(true, true).slideUp(300);
        isHidden = true;
      }
    } else if (scrollTop < lastScrollTop) {
      // scrolling up → show
      if (isHidden) {
        $navTopRow.stop(true, true).slideDown(300);
        isHidden = false;
      }
    }

    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // avoid negative values
  });
});
