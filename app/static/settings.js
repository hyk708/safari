document.addEventListener("DOMContentLoaded", async function () {
    const categoryList = document.getElementById("resultList");
    const userInput = document.getElementById("userInput");
    const presetList = document.getElementById("presetList");
    const authBtn = document.getElementById("auth-btn");
    let token = localStorage.getItem("access_token");

    async function checkLoginStatus() {
        try {
            const response = await fetch("http://localhost:8000/auth/me", {
                credentials: "include",
                headers: { Authorization: `Bearer ${token}` }
            });

            if (!response.ok) {
                throw new Error("Unauthorized");
            }

            const user = await response.json();
            console.log("로그인 사용자:", user);
            document.getElementById("user-info").innerText = `${user.username}님 안녕하세요!`;
            authBtn.innerText = "로그아웃";
            authBtn.onclick = logout;
        } catch (error) {
            console.warn("로그인 필요:", error);
            // 🚨 로그인 필요하지만 자동으로 `/login`으로 보내지는 않도록 수정
        }
    }

    async function logout() {
        try {
            await fetch("http://localhost:8000/auth/logout", {
                method: "POST",
                credentials: "include"
            });
            localStorage.removeItem("access_token");
            window.location.href = "/";
        } catch (error) {
            console.error("로그아웃 실패:", error);
        }
    }

    async function fetchCategories() {
        try {
            const response = await fetch("http://localhost:8000/categories/", {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (!response.ok) throw new Error("카테고리 로드 실패");

            const data = await response.json();
            categoryList.innerHTML = "";

            data.categories.forEach(category => {
                const li = document.createElement("li");
                li.className = "list-group-item d-flex justify-content-between align-items-center";
                li.innerHTML = `
                    <span>${category.name}</span>
                    <div>
                        <button class="btn btn-warning btn-sm edit-btn" data-id="${category.id}">수정</button>
                        <button class="btn btn-danger btn-sm delete-btn" data-id="${category.id}">삭제</button>
                    </div>
                `;
                categoryList.appendChild(li);
            });

            document.querySelectorAll(".edit-btn").forEach(button => {
                button.addEventListener("click", () => updateCategory(button.dataset.id));
            });

            document.querySelectorAll(".delete-btn").forEach(button => {
                button.addEventListener("click", () => deleteCategory(button.dataset.id));
            });

        } catch (error) {
            console.error("카테고리 조회 오류:", error);
        }
    }

    checkLoginStatus();
    fetchCategories();
});
