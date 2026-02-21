<script>
    import {
        Card,
        Label,
        Input,
        Textarea,
        Button,
    } from 'flowbite-svelte';

    export let data;
</script>
<div class="grid gap-4 p-4 w-full">
    <Card size="none">
        <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900">이메일 보내기</h5>
        <form method="POST" action="?/email">
            <div class="grid gap-6 grid-col mb-6">
                <div class="grid gap-2">
                    <Label>제목</Label>
                    <Input type="text" name="subject" />
                </div>
                <div class="grid gap-2">
                    <Label>내용</Label>
                    <Textarea rows="20" name="body" />
                </div>
            </div>
            <Button type="submit" color="blue" size="xl" class="w-full">보내기</Button>
        </form>
    </Card>
</div>