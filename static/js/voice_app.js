const API = '';
let token = localStorage.getItem('token');
let recognition = null;
let isRecording = false;

window.onload = () => {
  if (token) showUserMenu();
  loadCategories();
  loadProducts();
  initSpeechRecognition();
};

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    document.getElementById('voiceStatus').textContent = '⚠️ Voice not supported in this browser (use Chrome)';
    return;
  }
  recognition = new SpeechRecognition();
  recognition.lang = 'en-IN';
  recognition.continuous = false;
  recognition.interimResults = true;

  recognition.onstart = () => {
    isRecording = true;
    document.getElementById('micBtn').classList.add('recording');
    document.getElementById('voiceStatus').textContent = '🔴 Listening...';
  };
  recognition.onresult = (e) => {
    const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
    document.getElementById('voiceTranscript').textContent = `"${transcript}"`;
    if (e.results[e.results.length - 1].isFinal) sendVoiceCommand(transcript);
  };
  recognition.onend = () => {
    isRecording = false;
    document.getElementById('micBtn').classList.remove('recording');
    document.getElementById('voiceStatus').textContent = '🎤 Click mic to talk to VoiceShop AI';
  };
  recognition.onerror = (e) => {
    console.error('Speech error:', e.error);
    recognition.stop();
  };
}

function toggleVoice() {
  if (!token) { alert('Please login to use voice features!'); return; }
  if (!recognition) return;
  isRecording ? recognition.stop() : recognition.start();
}

async function sendVoiceCommand(transcript) {
  try {
    const res = await fetch(`${API}/api/voice/command`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ transcript })
    });
    const data = await res.json();
    handleVoiceResponse(data);
  } catch (err) {
    showAIMessage('Sorry, I had trouble processing that. Please try again.');
  }
}

function handleVoiceResponse(data) {
  showAIMessage(data.message || 'Done!');
  speak(data.message || '');

  if (data.intent === 'search_products' && data.products) {
    renderProducts(data.products);
    document.getElementById('sectionTitle').textContent = `Voice Search: "${document.getElementById('voiceTranscript').textContent}"`;
  } else if (data.intent === 'add_to_cart') {
    updateCartCount(data.cart_count);
  } else if (data.intent === 'view_cart') {
    showCart();
  } else if (data.trigger_checkout) {
    closeCart();
    showModal('checkoutModal');
  }
}

function speak(text) {
  if (!text) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'en-IN';
  utter.rate = 0.95;
  window.speechSynthesis.speak(utter);
}

// ─── PRODUCTS ────────────────────────────────────────────────
async function loadProducts(query = '', category = '') {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  if (category) params.append('category', category);
  const res = await fetch(`${API}/api/products/?${params}`);
  const products = await res.json();
  renderProducts(products);
}

function renderProducts(products) {
  const grid = document.getElementById('productsGrid');
  if (!products.length) { grid.innerHTML = '<p style="color:#999;grid-column:1/-1">No products found.</p>'; return; }
  grid.innerHTML = products.map(p => `
    <div class="product-card">
      <img src="${p.image || 'https://via.placeholder.com/300x300?text=Product'}" alt="${p.name}" loading="lazy">
      <div class="product-info">
        <div class="product-name">${p.name}</div>
        <div class="product-category">${p.category}</div>
        <div class="product-price">₹${p.price.toLocaleString()}</div>
        <button class="btn-add-cart" onclick="addToCart('${p._id}', '${p.name}')">Add to Cart 🛒</button>
      </div>
    </div>`).join('');
}

async function loadCategories() {
  const res = await fetch(`${API}/api/products/categories`);
  const cats = await res.json();
  const div = document.getElementById('categories');
  div.innerHTML = ['All', ...cats].map((c, i) => `
    <button class="cat-btn ${i === 0 ? 'active' : ''}" onclick="filterCategory('${c}', this)">${c}</button>`
  ).join('');
}

function filterCategory(cat, btn) {
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  if (cat === 'All') { loadProducts(); document.getElementById('sectionTitle').textContent = 'All Products'; }
  else { loadProducts('', cat); document.getElementById('sectionTitle').textContent = cat; }
}

function searchProducts(q) { loadProducts(q); }

// ─── CART ────────────────────────────────────────────────────
async function addToCart(productId, name) {
  if (!token) { alert('Please login first!'); return; }
  const res = await fetch(`${API}/api/cart/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ product_id: productId, quantity: 1 })
  });
  const data = await res.json();
  updateCartCount(data.cart_count);
  showAIMessage(`✅ "${name}" added to cart!`);
}

async function showCart() {
  if (!token) { alert('Please login!'); return; }
  const res = await fetch(`${API}/api/cart/`, { headers: { 'Authorization': `Bearer ${token}` } });
  const data = await res.json();
  const itemsDiv = document.getElementById('cartItems');
  if (!data.items.length) { itemsDiv.innerHTML = '<p style="color:#999;text-align:center;margin-top:40px">Your cart is empty 🛒</p>'; }
  else {
    itemsDiv.innerHTML = data.items.map(item => `
      <div class="cart-item">
        <img src="${item.image || 'https://via.placeholder.com/60x60?text=P'}" alt="${item.name}">
        <div class="cart-item-info">
          <div class="cart-item-name">${item.name}</div>
          <div class="cart-item-price">₹${item.price.toLocaleString()} × ${item.quantity} = ₹${item.total.toLocaleString()}</div>
        </div>
        <button class="cart-item-remove" onclick="removeFromCart('${item.product_id}')">🗑</button>
      </div>`).join('');
  }
  document.getElementById('cartTotal').textContent = `₹${data.total.toLocaleString()}`;
  document.getElementById('cartSidebar').classList.add('open');
  document.getElementById('cartOverlay').classList.add('open');
}

function closeCart() {
  document.getElementById('cartSidebar').classList.remove('open');
  document.getElementById('cartOverlay').classList.remove('open');
}

async function removeFromCart(productId) {
  await fetch(`${API}/api/cart/remove/${productId}`, {
    method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` }
  });
  showCart();
}

function updateCartCount(count) {
  document.getElementById('cartCount').textContent = count || '';
}

// ─── CHECKOUT ────────────────────────────────────────────────
function showCheckout() { closeCart(); showModal('checkoutModal'); }

async function placeOrder() {
  const address = document.getElementById('checkoutAddress').value;
  const payment_method = document.getElementById('paymentMethod').value;
  if (!address) { alert('Please enter delivery address'); return; }
  const res = await fetch(`${API}/api/orders/checkout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ address, payment_method })
  });
  const data = await res.json();
  if (res.ok) {
    closeModal('checkoutModal');
    document.getElementById('successMsg').textContent = `Order #${data.order_id} confirmed! Total: ₹${data.total.toLocaleString()}`;
    showModal('successModal');
    updateCartCount(0);
    speak(`Your order has been placed! Total amount is ${data.total} rupees.`);
  }
}

// ─── AUTH ─────────────────────────────────────────────────────
async function login() {
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const res = await fetch(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  if (res.ok) { token = data.token; localStorage.setItem('token', token); showUserMenu(data.name); closeModal('loginModal'); }
  else alert(data.error);
}

async function register() {
  const name = document.getElementById('regName').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;
  const res = await fetch(`${API}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  });
  const data = await res.json();
  if (res.ok) { token = data.token; localStorage.setItem('token', token); showUserMenu(data.name); closeModal('registerModal'); }
  else alert(data.error);
}

function logout() { token = null; localStorage.removeItem('token'); location.reload(); }

function showUserMenu(name) {
  name = name || 'User';
  document.getElementById('authButtons').style.display = 'none';
  document.getElementById('userMenu').style.display = 'flex';
  document.getElementById('userName').textContent = `👋 ${name}`;
}

// ─── UTILS ────────────────────────────────────────────────────
function showAIMessage(msg) {
  document.getElementById('aiMessage').textContent = msg;
  document.getElementById('aiBubble').style.display = 'flex';
  setTimeout(() => document.getElementById('aiBubble').style.display = 'none', 5000);
}

function showModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }