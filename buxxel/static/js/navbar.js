$(function() {
  let lastScrollTop = 0;
  const $navbar = $("#mainNavbar"); // target your specific navbar
  const threshold = 50;             // optional scroll threshold
  let isHidden = false;

  $(window).on("scroll", function() {
    let scrollTop = $(this).scrollTop();

    if (scrollTop > lastScrollTop && scrollTop > threshold) {
      if (!isHidden) {
        $navbar.addClass("hidden"); // hide navbar
        isHidden = true;
      }
    } else if (scrollTop < lastScrollTop) {
      if (isHidden) {
        $navbar.removeClass("hidden"); // show navbar
        isHidden = false;
      }
    }

    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
  });
});
