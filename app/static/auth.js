document.addEventListener("DOMContentLoaded", async function () {
    const authBtn = document.getElementById("auth-btn");
    const userInfo = document.getElementById("user-info");

    async function checkLoginStatus() {
        try {
            const response = await fetch("http://localhost:8000/auth/me", {
                credentials: "include",  // ✅ 쿠키 포함
            });

            if (!response.ok) {
                throw new Error("Unauthorized");
            }

            const user = await response.json();
            console.log("로그인 성공:", user);
            userInfo.innerText = `${user.username}님 안녕하세요!`;
            authBtn.innerText = "로그아웃";
            authBtn.onclick = logout;
        } catch (error) {
            console.warn("로그인 필요:", error);
        }
    }

    async function logout() {
        try {
            await fetch("http://localhost:8000/auth/logout", {
                method: "POST",
                credentials: "include",
            });
            localStorage.removeItem("access_token");  // ✅ 토큰 제거
            window.location.href = "/";
        } catch (error) {
            console.error("로그아웃 실패:", error);
        }
    }

    checkLoginStatus();
});
