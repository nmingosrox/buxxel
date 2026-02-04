$(function() {
  let lastScrollTop = 0;
  const $navbar = $(".navbar"); // animate the whole navbar
  const threshold = 50;
  let isHidden = false;

  $(window).on("scroll", function() {
    let scrollTop = $(this).scrollTop();

    if (scrollTop > lastScrollTop && scrollTop > threshold) {
      if (!isHidden) {
        $navbar.stop(true, true).slideUp(300);
        isHidden = true;
      }
    } else if (scrollTop < lastScrollTop) {
      if (isHidden) {
        $navbar.stop(true, true).slideDown(300);
        isHidden = false;
      }
    }

    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
  });
});
