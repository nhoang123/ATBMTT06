document.addEventListener('DOMContentLoaded', function() {
    // Hiệu ứng fade-in cho card
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => card.classList.add('fade-in'));

    // Hiệu ứng focus input
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.backgroundColor = '#eaf6fb';
        });
        input.addEventListener('blur', function() {
            this.style.backgroundColor = '';
        });
    });

    // Tạo khóa RSA tự động khi nhấn nút
    const genKeyBtn = document.getElementById('gen-key-btn');
    if (genKeyBtn) {
        genKeyBtn.addEventListener('click', async function() {
            genKeyBtn.disabled = true;
            genKeyBtn.textContent = 'Đang sinh khóa...';
            // Sinh khóa bằng Web Crypto API (chỉ hỗ trợ trên trình duyệt hiện đại)
            try {
                const keyPair = await window.crypto.subtle.generateKey(
                    {
                        name: 'RSA-PSS',
                        modulusLength: 2048,
                        publicExponent: new Uint8Array([1, 0, 1]),
                        hash: 'SHA-256',
                    },
                    true,
                    ['sign', 'verify']
                );
                // Export private key PEM
                const exported = await window.crypto.subtle.exportKey('pkcs8', keyPair.privateKey);
                const pem = arrayBufferToPem(exported, 'PRIVATE KEY');
                document.getElementById('private_key').value = pem;
                // Lưu vào localStorage
                localStorage.setItem('private_key', pem);
                genKeyBtn.textContent = 'Đã sinh khóa!';
            } catch (e) {
                alert('Trình duyệt không hỗ trợ sinh khóa RSA tự động. Vui lòng nhập thủ công!');
                genKeyBtn.textContent = 'Sinh khóa tự động';
            }
            genKeyBtn.disabled = false;
        });
    }

    function arrayBufferToPem(buffer, label) {
        const binary = String.fromCharCode.apply(null, new Uint8Array(buffer));
        const base64 = window.btoa(binary);
        const lines = base64.match(/.{1,64}/g).join('\n');
        return `-----BEGIN ${label}-----\n${lines}\n-----END ${label}-----`;
    }
});
