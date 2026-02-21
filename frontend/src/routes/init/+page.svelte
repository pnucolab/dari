<script>
    import { enhance } from '$app/forms';
    import {
        Card,
        Heading,
        Label,
        Input,
        Fileupload,
        Button,
        Alert,
    } from 'flowbite-svelte';

    export let data;
    export let form;

    let currentStep = data.user ? 2 : 1;
    let submitting = false;

    // Store admin info client-side
    let adminUsername = '';
    let adminName = '';
    let adminEmail = '';
    let adminPassword = '';
    let adminPasswordConfirm = '';
    let step1Error = '';

    function goToStep2() {
        step1Error = '';

        if (!/^[a-z][a-z0-9]{0,30}$/.test(adminUsername)) {
            step1Error = '사용자명 형식이 올바르지 않습니다. 영문 소문자로 시작하며, 영문 소문자와 숫자만 포함해야 합니다 (1-31자)';
            return;
        }
        if (adminUsername.startsWith('guest')) {
            step1Error = '사용자명은 "guest"로 시작할 수 없습니다';
            return;
        }
        if (adminPassword.length < 8) {
            step1Error = '비밀번호는 최소 8자 이상이어야 합니다';
            return;
        }
        if (adminPassword !== adminPasswordConfirm) {
            step1Error = '비밀번호가 일치하지 않습니다';
            return;
        }

        currentStep = 2;
    }

    function handleDefaultsSubmit() {
        submitting = true;
        return async ({ result, update }) => {
            await update();
            submitting = false;
        };
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
    <div class="w-full max-w-3xl">
        <div class="mb-8">
            <div class="flex items-center justify-center">
                <div class="flex items-center space-x-4">
                    <div class="flex items-center">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold
                            {currentStep >= 1 ? 'bg-blue-600' : 'bg-gray-400'}">
                            {#if currentStep >= 2}
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                </svg>
                            {:else}
                                1
                            {/if}
                        </div>
                        <span class="ml-2 font-medium {currentStep >= 1 ? 'text-blue-600' : 'text-gray-500'}">
                            관리자 생성
                        </span>
                    </div>
                    <div class="w-16 h-0.5 {currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-300'}"></div>
                    <div class="flex items-center">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold
                            {currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-400'}">
                            2
                        </div>
                        <span class="ml-2 font-medium {currentStep >= 2 ? 'text-blue-600' : 'text-gray-500'}">
                            시스템 설정
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <Card size="xl" class="shadow-xl">
            {#if currentStep === 1}
                <div class="space-y-6">
                    <div class="text-center">
                        <Heading tag="h3" class="text-2xl font-semibold text-gray-800 mb-2">관리자 계정 생성</Heading>
                    </div>

                    <div class="space-y-5">
                        <div class="space-y-2">
                            <Label for="username" class="text-gray-700 font-medium">사용자명</Label>
                            <Input type="text" id="username" bind:value={adminUsername} required
                                   placeholder="영문 소문자와 숫자만 사용" class="text-base" />
                            <p class="text-sm text-gray-500">영문 소문자로 시작하며, 영문 소문자와 숫자만 포함해야 합니다</p>
                        </div>
                        <div class="space-y-2">
                            <Label for="name" class="text-gray-700 font-medium">이름</Label>
                            <Input type="text" id="name" bind:value={adminName} required placeholder="성함을 입력하세요" class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label for="email" class="text-gray-700 font-medium">이메일</Label>
                            <Input type="email" id="email" bind:value={adminEmail} required placeholder="admin@example.com" class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label for="password" class="text-gray-700 font-medium">비밀번호</Label>
                            <Input type="password" id="password" bind:value={adminPassword} required class="text-base" />
                            <p class="text-sm text-gray-500">최소 8자 이상</p>
                        </div>
                        <div class="space-y-2">
                            <Label for="password_confirm" class="text-gray-700 font-medium">비밀번호 확인</Label>
                            <Input type="password" id="password_confirm" bind:value={adminPasswordConfirm} required class="text-base" />
                        </div>

                        {#if step1Error}
                        <Alert color="red" class="mt-4">{step1Error}</Alert>
                        {/if}

                        <div class="pt-4">
                            <Button on:click={goToStep2} color="blue" size="xl" class="w-full">다음</Button>
                        </div>
                    </div>
                </div>
            {:else}
                <div class="space-y-6">
                    <div class="text-center">
                        <Heading tag="h3" class="text-2xl font-semibold text-gray-800 mb-2">시스템 설정</Heading>
                    </div>

                    <form method="POST" enctype="multipart/form-data" action="?/setup" use:enhance={handleDefaultsSubmit} class="space-y-5">
                        <input type="hidden" name="admin_username" value={adminUsername} />
                        <input type="hidden" name="admin_name" value={adminName} />
                        <input type="hidden" name="admin_email" value={adminEmail} />
                        <input type="hidden" name="admin_password" value={adminPassword} />

                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">기관 로고 (선택사항)</Label>
                            <Fileupload name="logo" />
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">기관명</Label>
                            <Input type="text" name="sitename" required placeholder="조직 이름을 입력하세요" class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">기본 Linux 그룹</Label>
                            <Input type="text" name="gid" placeholder="users" required class="text-base" />
                            <p class="text-sm text-gray-500">새 Linux 계정의 기본 그룹</p>
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">기본 셸</Label>
                            <Input type="text" name="shell" value="/bin/zsh" required class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">허용 이메일 도메인 (선택사항)</Label>
                            <Input type="text" name="allowed_email_domains" placeholder="example.com,university.ac.kr" class="text-base" />
                            <p class="text-sm text-gray-500">쉼표로 구분. 비워두면 모든 이메일 도메인 허용</p>
                        </div>

                        {#if form?.error}
                        <Alert color="red" class="mt-4">{form.error}</Alert>
                        {/if}

                        {#if form?.success}
                        <Alert color="green" class="mt-4">설정이 저장되었습니다! 관리자 페이지로 이동합니다...</Alert>
                        {/if}

                        <div class="pt-4 flex gap-3">
                            <Button on:click={() => currentStep = 1} color="alternative" size="xl" class="flex-1">이전</Button>
                            {#if submitting}
                                <Button color="green" size="xl" disabled class="flex-1">설정 중...</Button>
                            {:else}
                                <Button type="submit" color="green" size="xl" class="flex-1">설정 완료</Button>
                            {/if}
                        </div>
                    </form>
                </div>
            {/if}
        </Card>
    </div>
</div>
