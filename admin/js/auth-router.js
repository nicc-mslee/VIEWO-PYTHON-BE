/**
 * Viewo Admin - 인증 및 라우터 모듈
 * JWT Access Token / Refresh Token 기반 인증
 * Hash 기반 라우팅
 */

const Auth = {
    // 토큰 저장 키
    ACCESS_TOKEN_KEY: 'viewo_access_token',
    REFRESH_TOKEN_KEY: 'viewo_refresh_token',
    USER_KEY: 'viewo_user',

    // 토큰 갱신 타이머
    refreshTimer: null,

    /**
     * Access Token 저장
     */
    setAccessToken(token) {
        localStorage.setItem(this.ACCESS_TOKEN_KEY, token);
    },

    /**
     * Access Token 가져오기
     */
    getAccessToken() {
        return localStorage.getItem(this.ACCESS_TOKEN_KEY);
    },

    /**
     * Refresh Token 저장
     */
    setRefreshToken(token) {
        localStorage.setItem(this.REFRESH_TOKEN_KEY, token);
    },

    /**
     * Refresh Token 가져오기
     */
    getRefreshToken() {
        return localStorage.getItem(this.REFRESH_TOKEN_KEY);
    },

    /**
     * 사용자 정보 저장
     */
    setUser(user) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    },

    /**
     * 사용자 정보 가져오기
     */
    getUser() {
        try {
            const user = localStorage.getItem(this.USER_KEY);
            return user ? JSON.parse(user) : null;
        } catch {
            return null;
        }
    },

    /**
     * 모든 인증 정보 삭제
     */
    clearAuth() {
        localStorage.removeItem(this.ACCESS_TOKEN_KEY);
        localStorage.removeItem(this.REFRESH_TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    },

    /**
     * 로그인 여부 확인
     */
    isLoggedIn() {
        return !!this.getAccessToken();
    },

    /**
     * Access Token 디코딩 (만료 시간 확인용)
     */
    decodeToken(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch {
            return null;
        }
    },

    /**
     * Access Token 만료 여부 확인
     */
    isTokenExpired(token) {
        const payload = this.decodeToken(token);
        if (!payload || !payload.exp) return true;
        // 만료 1분 전부터 만료로 처리
        return (payload.exp * 1000) < (Date.now() + 60000);
    },

    /**
     * Access Token 자동 갱신 스케줄링
     */
    scheduleTokenRefresh() {
        const token = this.getAccessToken();
        if (!token) return;

        const payload = this.decodeToken(token);
        if (!payload || !payload.exp) return;

        const expiresAt = payload.exp * 1000;
        const now = Date.now();
        // 만료 2분 전에 갱신
        const refreshTime = expiresAt - now - 120000;

        if (refreshTime > 0) {
            this.refreshTimer = setTimeout(() => {
                this.refreshAccessToken();
            }, refreshTime);
        } else if (refreshTime > -60000) {
            // 만료 직전이면 즉시 갱신
            this.refreshAccessToken();
        }
    },

    /**
     * Access Token 갱신
     */
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            this.handleAuthError();
            return false;
        }

        try {
            const response = await fetch(`${API_BASE}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            const data = await response.json();

            if (data.success && data.access_token) {
                this.setAccessToken(data.access_token);
                this.scheduleTokenRefresh();
                return true;
            } else {
                this.handleAuthError();
                return false;
            }
        } catch (error) {
            console.error('토큰 갱신 실패:', error);
            this.handleAuthError();
            return false;
        }
    },

    /**
     * 인증 오류 처리 (로그아웃)
     */
    handleAuthError() {
        this.clearAuth();
        Router.navigate('login');
        if (typeof showToast === 'function') {
            showToast('세션이 만료되었습니다. 다시 로그인해주세요.', 'error');
        }
    },

    /**
     * 로그인
     */
    async login(username, password) {
        try {
            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                this.setAccessToken(data.access_token);
                this.setRefreshToken(data.refresh_token);
                this.setUser(data.user);
                this.scheduleTokenRefresh();
                return { success: true, user: data.user };
            } else {
                return { success: false, message: data.message || '로그인에 실패했습니다.' };
            }
        } catch (error) {
            console.error('로그인 오류:', error);
            return { success: false, message: '서버에 연결할 수 없습니다.' };
        }
    },

    /**
     * 로그아웃
     */
    async logout() {
        const refreshToken = this.getRefreshToken();

        if (refreshToken) {
            try {
                await fetch(`${API_BASE}/auth/logout`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken })
                });
            } catch (error) {
                console.error('로그아웃 API 오류:', error);
            }
        }

        this.clearAuth();
    },

    /**
     * API 요청 헤더 (Authorization 포함)
     */
    getAuthHeaders() {
        const token = this.getAccessToken();
        if (token) {
            return { 'Authorization': `Bearer ${token}` };
        }
        return {};
    },

    /**
     * 인증된 fetch 요청
     */
    async authFetch(url, options = {}) {
        // 토큰 만료 확인 및 갱신
        const token = this.getAccessToken();
        if (token && this.isTokenExpired(token)) {
            const refreshed = await this.refreshAccessToken();
            if (!refreshed) {
                throw new Error('인증이 만료되었습니다.');
            }
        }

        // 헤더에 Authorization 추가
        const headers = {
            ...options.headers,
            ...this.getAuthHeaders()
        };

        const response = await fetch(url, { ...options, headers });

        // 401 응답 시 토큰 갱신 시도
        if (response.status === 401) {
            const refreshed = await this.refreshAccessToken();
            if (refreshed) {
                // 재시도
                const retryHeaders = {
                    ...options.headers,
                    ...this.getAuthHeaders()
                };
                return fetch(url, { ...options, headers: retryHeaders });
            } else {
                this.handleAuthError();
                throw new Error('인증이 만료되었습니다.');
            }
        }

        return response;
    },

    /**
     * 초기화 (앱 시작 시 호출)
     */
    init() {
        if (this.isLoggedIn()) {
            const token = this.getAccessToken();
            if (this.isTokenExpired(token)) {
                // 토큰 만료 시 갱신 시도
                this.refreshAccessToken().then(success => {
                    if (!success) {
                        Router.navigate('login');
                    } else {
                        this.scheduleTokenRefresh();
                    }
                });
            } else {
                this.scheduleTokenRefresh();
            }
        }
    }
};


/**
 * Hash 기반 라우터
 */
const Router = {
    routes: {
        'login': 'showLoginPage',
        'dashboard': 'showDashboardPage',
        'slides': 'showSlidesPage',
        'buildings': 'showBuildingsPage',
        'floor-plan': 'showFloorPlanPage',
        'clients': 'showClientsPage',
        'settings': 'showSettingsPage',
        'departments': 'showDepartmentsPage'
    },

    // 인증이 필요하지 않은 라우트
    publicRoutes: ['login'],

    // 현재 라우트
    currentRoute: null,

    /**
     * 라우터 초기화
     */
    init() {
        // hashchange 이벤트 리스닝
        window.addEventListener('hashchange', () => this.handleRoute());

        // 초기 라우팅
        this.handleRoute();
    },

    /**
     * 현재 해시에서 라우트 추출
     */
    getRouteFromHash() {
        const hash = window.location.hash.slice(1) || 'dashboard';
        return hash.split('?')[0]; // 쿼리 스트링 제거
    },

    /**
     * 라우트 변경
     */
    navigate(route, replace = false) {
        if (replace) {
            window.location.replace(`#${route}`);
        } else {
            window.location.hash = route;
        }
    },

    /**
     * 라우트 처리
     */
    handleRoute() {
        let route = this.getRouteFromHash();

        // 인증 체크
        if (!this.publicRoutes.includes(route) && !Auth.isLoggedIn()) {
            this.navigate('login', true);
            return;
        }

        // 로그인 상태에서 login 페이지 접근 시 대시보드로
        if (route === 'login' && Auth.isLoggedIn()) {
            this.navigate('dashboard', true);
            return;
        }

        // 라우트가 없으면 기본값
        if (!this.routes[route]) {
            route = Auth.isLoggedIn() ? 'dashboard' : 'login';
            this.navigate(route, true);
            return;
        }

        this.currentRoute = route;

        // 페이지 표시
        if (route === 'login') {
            this.showLoginPage();
        } else {
            this.showAppPage(route);
        }

        // 사이드바 네비게이션 업데이트
        this.updateNavigation(route);
    },

    /**
     * 로그인 페이지 표시
     */
    showLoginPage() {
        document.getElementById('loginPage').style.display = 'flex';
        document.getElementById('dashboard').classList.remove('show');
    },

    /**
     * 앱 메인 페이지 표시
     */
    showAppPage(route) {
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('dashboard').classList.add('show');

        // 사용자 정보 업데이트
        const user = Auth.getUser();
        if (user) {
            const avatarEl = document.getElementById('userAvatar');
            const nameEl = document.getElementById('userName');
            if (avatarEl) avatarEl.textContent = user.name ? user.name[0] : '관';
            if (nameEl) nameEl.textContent = user.name || user.username;
        }

        // showPage 함수 호출 (기존 코드와 호환)
        if (typeof showPage === 'function') {
            showPage(route);
        }
    },

    /**
     * 네비게이션 업데이트
     */
    updateNavigation(route) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === route) {
                item.classList.add('active');
            }
        });
    }
};


// 전역으로 내보내기
window.Auth = Auth;
window.Router = Router;
