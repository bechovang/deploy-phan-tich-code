// static/js/result.js
document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM loaded, checking for confetti conditions...");
  
  // Kiểm tra xem đã tải thư viện confetti hay chưa
  if (typeof confetti === 'undefined') {
    console.error("Confetti library is not loaded! Please add the library script tag before this script.");
    return;
  }

  const container = document.querySelector('.container');
  if (!container) {
    console.error("Container element not found");
    return;
  }
  
  console.log("Container found, analysis present:", container.dataset.analysisPresent);
  
  if (container.dataset.analysisPresent !== 'true') {
    console.log("No analysis present, not showing confetti");
    return;
  }

  // Log để debug các giá trị
  const meets = JSON.parse(container.dataset.meetsRequirements || 'false');
  const seCnt = +(container.dataset.syntaxErrorsCount || 0);
  const leCnt = +(container.dataset.logicalErrorsCount || 0);
  const piCnt = +(container.dataset.potentialIssuesCount || 0);
  
  console.log("Conditions for confetti:", {
    meets: meets,
    syntaxErrors: seCnt,
    logicalErrors: leCnt,
    potentialIssues: piCnt,
    confettiExists: typeof confetti === 'function'
  });

  // Chỉ bắn confetti khi code hoàn toàn đúng
  if (!(meets && seCnt === 0 && leCnt === 0 && piCnt === 0)) {
    console.log("Code has errors or potential issues, not showing confetti");
    return;
  }
  
  console.log("All conditions met! Launching confetti...");

  try {
    // Tạo một instance confetti dùng worker để performance tốt hơn
    const myConfetti = confetti.create(document.createElement('canvas'), {
      resize: true,
      useWorker: true
    });

    // Mảng màu rực rỡ
    const colors = [
      '#ff595e',
      '#ffca3a',
      '#8ac926',
      '#1982c4',
      '#6a4c93',
      '#f72585',
      '#3a0ca3'
    ];

    // Bắn confetti ngay lập tức khi điều kiện đúng
    launchInitialConfetti();

    // Hàm bắn một đợt confetti lớn ngay lập tức
    function launchInitialConfetti() {
      myConfetti({
        particleCount: 200,
        spread: 100,
        origin: { y: 0.6 }
      });
    }

    // Hàm bắn một đợt confetti
    function launchBurst() {
      myConfetti({
        particleCount: 100,
        angle: Math.random() * 60 + 60,        // góc giữa 60–120°
        spread: Math.random() * 60 + 40,       // độ tỏa giữa 40–100°
        startVelocity: Math.random() * 30 + 20,// vận tốc ban đầu
        origin: {
          x: Math.random(),
          y: Math.random() * 0.2              // chỗ cao đầu
        },
        colors: colors,
        scalar: Math.random() * 0.6 + 0.7      // kích thước thay đổi
      });
    }

    // Bắn liên tục mỗi 500ms
    const confettiInterval = setInterval(launchBurst, 500);

    // Tự động dừng sau 5 giây
    setTimeout(() => {
      clearInterval(confettiInterval);
      console.log("Confetti automatically stopped after 5 seconds");
    }, 5000);

    // Hoặc dừng khi người dùng click bất kỳ đâu
    function stopConfetti() {
      clearInterval(confettiInterval);
      myConfetti.reset();
      console.log("Confetti stopped by user click");
      document.removeEventListener('click', stopConfetti);
    }
    document.addEventListener('click', stopConfetti);
  } catch (error) {
    console.error("Error while trying to launch confetti:", error);
  }
});