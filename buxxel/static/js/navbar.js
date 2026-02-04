$(function() {
  let lastScrollTop = 0;
  const $navbar = $(".navbar");
  const threshold = 50;
  let isHidden = false;

  $(window).on("scroll", function() {
    let scrollTop = $(this).scrollTop();

    if (scrollTop > lastScrollTop && scrollTop > threshold) {
      if (!isHidden) {
        $navbar.addClass("hidden");
        isHidden = true;
      }
    } else if (scrollTop < lastScrollTop) {
      if (isHidden) {
        $navbar.removeClass("hidden");
        isHidden = false;
      }
    }

    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
  });
});
