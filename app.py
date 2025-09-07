from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
import datetime
import json
import os
from werkzeug.utils import secure_filename
import hashlib
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Explicitly configure static file serving with absolute paths for reliability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.static_url_path = '/static'
app.static_folder = os.path.join(BASE_DIR, 'static')

# 用户与下载数据存储（SHA-256 哈希用户名/密码）
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
DOWNLOADS_FILE = os.path.join(BASE_DIR, 'downloads.json')

users_store = {}  # 哈希用户名 -> {password: 哈希, role: 'admin'|'user', display: 原名}
downloads_store = []  # [{name, url}]

def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_users():
    global users_store
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users_store = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users_store = {}

def save_users():
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_store, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving users: {e}")

def ensure_admin_exists():
    has_admin = any((u.get('role') == 'admin') for u in users_store.values())
    if not has_admin:
        username = 'cao'
        password = '3834193czy'
        hu = sha256_hex(username)
        hp = sha256_hex(password)
        users_store[hu] = {'password': hp, 'role': 'admin', 'display': username}
        save_users()
    
    # Create a test user for demonstration
    test_username = 'testuser'
    test_hu = sha256_hex(test_username)
    if test_hu not in users_store:
        users_store[test_hu] = {'password': sha256_hex('12345678'), 'role': 'user', 'display': test_username}
        save_users()

def register_user(username: str, password: str) -> str:
    if len(password or '') < 8:
        return '密码至少需要8位'
    hu = sha256_hex(username)
    if hu in users_store:
        return '用户名已存在'
    users_store[hu] = {'password': sha256_hex(password), 'role': 'user', 'display': username}
    save_users()
    return ''

def verify_user(username: str, password: str) -> bool:
    hu = sha256_hex(username)
    user = users_store.get(hu)
    if not user:
        return False
    return user.get('password') == sha256_hex(password)

def delete_user_record(username: str) -> bool:
    hu = sha256_hex(username)
    if hu in users_store:
        del users_store[hu]
        save_users()
        return True
    return False

def get_role(username: str) -> str:
    u = users_store.get(sha256_hex(username))
    return (u or {}).get('role', 'user')

def load_downloads():
    global downloads_store
    try:
        with open(DOWNLOADS_FILE, 'r', encoding='utf-8') as f:
            downloads_store = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        downloads_store = []

def save_downloads():
    try:
        with open(DOWNLOADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(downloads_store, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving downloads: {e}")

# Python小技巧列表
CODE_TIPS = [
    "使用列表推导式可以更简洁地创建列表：squares = [x**2 for x in range(10)]",
    "使用 f-strings 进行字符串格式化：name = 'World'; print(f'Hello, {name}!')",
    "使用 enumerate() 同时获取索引和值：for i, value in enumerate(['a', 'b', 'c']): print(i, value)",
    "使用 zip() 同时遍历多个列表：for a, b in zip(list1, list2): print(a, b)",
    "使用 with 语句自动管理资源：with open('file.txt', 'r') as f: content = f.read()",
    "使用 collections.defaultdict 简化字典操作：from collections import defaultdict; d = defaultdict(list)",
    "使用 any() 和 all() 检查条件：any(x > 0 for x in numbers)",
    "使用 set 去重：unique_items = set(items)",
    "使用 dict.get() 安全获取字典值：value = my_dict.get('key', 'default')",
    "使用 *args 和 **kwargs 处理可变参数：def func(*args, **kwargs): pass",
    "C++: 使用 auto 关键字简化类型声明。",
    "C++: 优先使用智能指针（如 std::unique_ptr, std::shared_ptr）管理内存。",
    "C++: 使用范围-based for 循环遍历容器。",
    "C++: 避免使用原始指针和手动内存管理。",
    "C++: 使用 const 正确标记不可修改的数据。",
    "JavaScript: 使用 === 进行严格相等比较，避免类型转换问题。",
    "JavaScript: 使用 let 和 const 替代 var。",
    "JavaScript: 箭头函数（=>）绑定 this 上下文。",
    "Git: 使用 git stash 暂存当前修改。",
    "Linux: 使用 grep 命令搜索文件内容。"
]

# 支持的语言
LANGUAGES = {
    'zh': '中文',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어',
    'ru': 'Русский',
    'es': 'Español'
}

LANG_TEXT = {
    'zh': {
        'site_name': '我的博客',
        'welcome': '欢迎来到我的博客',
        'skills': '技能：Python、C++、系统开发',
        'latest': '最新文章',
        'about': '关于我',
        'login': '登录/注册',
        'logout': '退出',
        'admin': '管理员',
        'footer': '我的博客',
        'back_home': '返回首页',
        'username': '用户名',
        'phone': '手机号/密码',
        'login_register': '登录/注册',
        'copyright': '我的博客',
        'tip_title': '小技巧',
        'language_switch': '语言切换',
        'theme': '配色方案',
        'light': '浅色',
        'dark': '深色',
        'delete_account': '注销账户',
        'confirm_delete_user': '确定要注销当前用户吗？此操作不可恢复！',
        'new_post': '新建文章',
        'title_label': '标题',
        'content_label': '内容',
        'publish_post': '发布文章',
        'upload_images': '上传图片 (最多 9 张)',
        'choose_images': '选择图片',
        'only_images_allowed': '只能选择图片文件。',
        'max_images_limit': '最多只能上传 {n} 张图片。',
        'edit_post': '修改文章',
        'delete_post': '删除文章',
        'confirm_delete_post': '确定要删除这篇文章吗？',
        'delete_success': '文章删除成功！',
        'delete_fail': '删除文章失败',
        'delete_error': '删除文章出错',
        'home': '首页',
        'games': '游戏',
        'join': '加入我们',
        'settings': '设置',
        'contact': '联系方式',
        'phone_label': '电话',
        'email_label': '邮箱',
        'collapse': '收起',
        'downloads': '相关下载',
        'new_download': '新增下载项',
        'software_name': '软件名称',
        'download_url': '下载链接',
        'twofa_code': '验证码',
        'users_list_title': '用户列表',
        'delete_user': '删除用户',
        'register': '注册',
        'password_required': '密码至少需要8位',
        'username_exists': '用户名已存在',
        'register_success': '注册成功',
        'login_success': '登录成功',
        'admin_login_success': '管理员登录成功',
        'verification_code_error': '验证码错误',
        'need_verification_code': '管理员登录需要验证码，请输入验证码',
        'password_error': '密码错误',
        'guest_login_success': '以游客身份登录成功',
        'post_published': '文章发布成功',
        'post_updated': '文章更新成功',
        'title_content_required': '标题和内容不能为空',
        'server_error': '服务器内部错误',
        'post_not_found': '文章未找到',
        'only_admin_create': '只有管理员才能创建文章',
        'only_admin_edit': '只有管理员才能编辑文章',
        'only_admin_delete': '只有管理员才能删除文章',
        'only_admin_upload': '只有管理员才能上传图片',
        'only_admin_add_download': '只有管理员才能新增下载',
        'only_admin_delete_user': '只有管理员才能删除用户',
        'cannot_delete_admin': '不能删除管理员',
        'user_not_found': '用户不存在',
        'user_deleted': '用户删除成功',
        'delete_failed': '删除失败',
        'confirm_delete_user_confirm': '确定要删除用户',
        'confirm_question': '吗？',
        'user_delete_success': '用户删除成功',
        'post_delete_success': '文章删除成功',
        'post_delete_failed': '删除文章失败',
        'post_delete_error': '删除文章出错',
        'confirm_delete_post_question': '确定要删除这篇文章吗？',
        'confirm_delete_user_question': '确定要删除用户',
        'confirm_delete_user_end': '吗？',
        'snake_game': '贪吃蛇',
        'tetris_game': '俄罗斯方块',
        'pacman_game': '吃豆人',
        'more_games': '更多游戏',
        'play_game': '开始游戏',
        'game_description_snake': '经典贪吃蛇游戏，使用方向键控制',
        'game_description_tetris': '经典俄罗斯方块，挑战你的反应速度',
        'game_description_pacman': '经典吃豆人，收集所有豆子',
        'game_description_more': '更多精彩游戏即将推出',
        'download_list': '下载列表',
        'no_downloads': '暂无下载内容',
        'add_download_item': '新增下载项',
        'software_name_placeholder': '请输入软件名称',
        'download_url_placeholder': '请输入下载链接',
        'name_url_required': '名称与链接不能为空',
        'download_added': '下载项添加成功',
        'game_controls': '游戏控制',
        'use_arrow_keys': '使用方向键控制',
        'press_r_restart': '按 R 重新开始',
        'score': '得分',
        'high_score': '最高分',
        'game_over': '游戏结束',
        'restart_game': '重新开始',
        'switch_account': '切换账户',
        'change_avatar': '更换头像',
        'change_account_name': '修改账户名',
        'batch_delete_users': '批量删除用户',
        'avatar_updated': '头像更新成功',
        'account_name_updated': '账户名更新成功',
        'back_downloads': '返回下载页',
        'breakout_game': '打砖块',
        'memory_game': '记忆翻牌',
        'sudoku_game': '数独',
        'minesweeper_game': '扫雷',
        'asteroids_game': '小行星',
        'pong_game': '乒乓球',
        'flappy_game': '飞翔小鸟',
        'game_description_breakout': '经典打砖块游戏，用球拍击球',
        'game_description_memory': '翻牌配对，挑战你的记忆力',
        'game_description_2048': '数字合并游戏，挑战2048',
        'game_description_sudoku': '经典数独谜题，锻炼逻辑思维',
        'game_description_minesweeper': '经典扫雷游戏，小心地雷',
        'game_description_asteroids': '太空射击游戏，击碎小行星',
        'game_description_pong': '经典乒乓球游戏，与AI对战',
        'game_description_flappy': '点击控制小鸟飞行，避开障碍',
        'tank_game': '疯狂坦克',
        'game_description_tank': '经典2D坦克对战游戏，选择玩家数量，控制坦克发射炮弹击败对手'
    },
    'en': {
        'site_name': 'My Blog',
        'welcome': 'Welcome to My Blog',
        'skills': 'Skills: Python, C++, System Development',
        'latest': 'Latest Posts',
        'about': 'About Me',
        'login': 'Login/Register',
        'logout': 'Logout',
        'admin': 'Admin',
        'footer': 'My Blog',
        'back_home': 'Back to Home',
        'username': 'Username',
        'phone': 'Phone/Password',
        'login_register': 'Login/Register',
        'copyright': 'My Blog',
        'tip_title': 'Tip',
        'language_switch': 'Language',
        'theme': 'Theme',
        'light': 'Light',
        'dark': 'Dark',
        'delete_account': 'Delete Account',
        'confirm_delete_user': 'Are you sure to delete this account? This cannot be undone!',
        'new_post': 'New Post',
        'title_label': 'Title',
        'content_label': 'Content',
        'publish_post': 'Publish',
        'upload_images': 'Upload Images (up to 9)',
        'choose_images': 'Choose Images',
        'only_images_allowed': 'Only image files are allowed.',
        'max_images_limit': 'You can upload at most {n} images.',
        'edit_post': 'Edit Post',
        'delete_post': 'Delete Post',
        'confirm_delete_post': 'Are you sure you want to delete this post?',
        'delete_success': 'Post deleted successfully!',
        'delete_fail': 'Failed to delete the post',
        'delete_error': 'An error occurred while deleting the post',
        'home': 'Home',
        'games': 'Games',
        'join': 'Join Us',
        'settings': 'Settings',
        'contact': 'Contact',
        'phone_label': 'Phone',
        'email_label': 'Email',
        'collapse': 'Collapse',
        'downloads': 'Downloads',
        'new_download': 'New Download',
        'software_name': 'Software Name',
        'download_url': 'Download URL',
        'twofa_code': 'Verification Code',
        'users_list_title': 'User List',
        'delete_user': 'Delete User',
        'register': 'Register',
        'password_required': 'Password must be at least 8 characters',
        'username_exists': 'Username already exists',
        'register_success': 'Registration successful',
        'login_success': 'Login successful',
        'admin_login_success': 'Admin login successful',
        'verification_code_error': 'Verification code error',
        'need_verification_code': 'Admin login requires verification code, please enter the code',
        'password_error': 'Password error',
        'guest_login_success': 'Logged in as guest successfully',
        'post_published': 'Post published successfully',
        'post_updated': 'Post updated successfully',
        'title_content_required': 'Title and content cannot be empty',
        'server_error': 'Server internal error',
        'post_not_found': 'Post not found',
        'only_admin_create': 'Only admin can create posts',
        'only_admin_edit': 'Only admin can edit posts',
        'only_admin_delete': 'Only admin can delete posts',
        'only_admin_upload': 'Only admin can upload images',
        'only_admin_add_download': 'Only admin can add downloads',
        'only_admin_delete_user': 'Only admin can delete users',
        'cannot_delete_admin': 'Cannot delete admin',
        'user_not_found': 'User not found',
        'user_deleted': 'User deleted successfully',
        'delete_failed': 'Delete failed',
        'confirm_delete_user_confirm': 'Are you sure to delete user',
        'confirm_question': '?',
        'user_delete_success': 'User deleted successfully',
        'post_delete_success': 'Post deleted successfully',
        'post_delete_failed': 'Failed to delete post',
        'post_delete_error': 'Error occurred while deleting post',
        'confirm_delete_post_question': 'Are you sure you want to delete this post?',
        'confirm_delete_user_question': 'Are you sure to delete user',
        'confirm_delete_user_end': '?',
        'snake_game': 'Snake',
        'tetris_game': 'Tetris',
        'pacman_game': 'Pac-Man',
        'more_games': 'More Games',
        'play_game': 'Play Game',
        'game_description_snake': 'Classic Snake game, use arrow keys to control',
        'game_description_tetris': 'Classic Tetris, challenge your reaction speed',
        'game_description_pacman': 'Classic Pac-Man, collect all dots',
        'game_description_more': 'More exciting games coming soon',
        'download_list': 'Download List',
        'no_downloads': 'No downloads available',
        'add_download_item': 'Add Download Item',
        'software_name_placeholder': 'Enter software name',
        'download_url_placeholder': 'Enter download URL',
        'name_url_required': 'Name and URL cannot be empty',
        'download_added': 'Download item added successfully',
        'game_controls': 'Game Controls',
        'use_arrow_keys': 'Use arrow keys to control',
        'press_r_restart': 'Press R to restart',
        'score': 'Score',
        'high_score': 'High Score',
        'game_over': 'Game Over',
        'restart_game': 'Restart Game',
        'switch_account': 'Switch Account',
        'change_avatar': 'Change Avatar',
        'change_account_name': 'Change Account Name',
        'batch_delete_users': 'Batch Delete Users',
        'avatar_updated': 'Avatar updated successfully',
        'account_name_updated': 'Account name updated successfully',
        'back_downloads': 'Back to Downloads',
        'breakout_game': 'Breakout',
        'memory_game': 'Memory Match',
        'sudoku_game': 'Sudoku',
        'minesweeper_game': 'Minesweeper',
        'asteroids_game': 'Asteroids',
        'pong_game': 'Pong',
        'flappy_game': 'Flappy Bird',
        'game_description_breakout': 'Classic Breakout game, use paddle to hit ball',
        'game_description_memory': 'Flip cards to match pairs, challenge your memory',
        'game_description_2048': 'Number merging game, challenge to reach 2048',
        'game_description_sudoku': 'Classic Sudoku puzzle, exercise logical thinking',
        'game_description_minesweeper': 'Classic Minesweeper game, watch out for mines',
        'game_description_asteroids': 'Space shooting game, destroy asteroids',
        'game_description_pong': 'Classic Pong game, play against AI',
        'game_description_flappy': 'Click to control bird flight, avoid obstacles',
        'tank_game': 'Crazy Tanks',
        'game_description_tank': 'Classic 2D tank battle game, choose player count, control tanks to defeat opponents'
    },
    'ja': {
        'site_name': '私のブログ',
        'welcome': '私のブログへようこそ',
        'skills': 'スキル：Python、C++、システム開発',
        'latest': '最新記事',
        'about': '私について',
        'login': 'ログイン/登録',
        'logout': 'ログアウト',
        'admin': '管理者',
        'footer': '私のブログ',
        'back_home': 'ホームへ戻る',
        'username': 'ユーザー名',
        'phone': '電話番号/パスワード',
        'login_register': 'ログイン/登録',
        'copyright': '私のブログ',
        'tip_title': 'ヒント',
        'language_switch': '言語切替',
        'theme': 'テーマ',
        'light': 'ライト',
        'dark': 'ダーク',
        'delete_account': 'アカウント削除',
        'confirm_delete_user': '本当にこのアカウントを削除しますか？この操作は元に戻せません。',
        'new_post': '新規記事',
        'title_label': 'タイトル',
        'content_label': '内容',
        'publish_post': '公開',
        'upload_images': '画像をアップロード（最大9枚）',
        'choose_images': '画像を選択',
        'only_images_allowed': '画像ファイルのみ選択できます。',
        'max_images_limit': '画像は最大 {n} 枚までアップロードできます。',
        'edit_post': '記事を編集',
        'delete_post': '記事を削除',
        'confirm_delete_post': 'この記事を削除してもよろしいですか？',
        'delete_success': '記事を削除しました！',
        'delete_fail': '記事の削除に失敗しました',
        'delete_error': '記事の削除中にエラーが発生しました',
        'home': 'ホーム',
        'games': 'ゲーム',
        'join': '参加する',
        'settings': '設定',
        'contact': '連絡先',
        'phone_label': '電話',
        'email_label': 'メール',
        'collapse': '折りたたむ',
        'downloads': 'ダウンロード',
        'new_download': 'ダウンロード追加',
        'software_name': 'ソフト名',
        'download_url': 'ダウンロードURL',
        'twofa_code': '認証コード',
        'switch_account': 'アカウント切り替え',
        'change_avatar': 'アバター変更',
        'change_account_name': 'アカウント名変更',
        'batch_delete_users': 'ユーザー一括削除',
        'avatar_updated': 'アバター更新成功',
        'account_name_updated': 'アカウント名更新成功',
        'back_downloads': 'ダウンロードに戻る',
        'breakout_game': 'ブロック崩し',
        'memory_game': '記憶ゲーム',
        'sudoku_game': '数独',
        'minesweeper_game': 'マインスイーパー',
        'asteroids_game': 'アステロイド',
        'pong_game': 'ポン',
        'flappy_game': 'フラッピーバード',
        'game_description_breakout': 'クラシックなブロック崩しゲーム',
        'game_description_memory': 'カードをめくってペアを見つける記憶ゲーム',
        'game_description_2048': '数字を合体させて2048を目指すゲーム',
        'game_description_sudoku': 'クラシックな数独パズル',
        'game_description_minesweeper': 'クラシックなマインスイーパーゲーム',
        'game_description_asteroids': '宇宙シューティングゲーム',
        'game_description_pong': 'クラシックなポンゲーム',
        'game_description_flappy': 'クリックで鳥を飛ばし、障害物を避ける',
        'tank_game': 'クレイジータンク',
        'game_description_tank': 'クラシックな2Dタンクバトルゲーム、プレイヤー数を選択して対戦'
    },
    'ko': {
        'site_name': '내 블로그',
        'welcome': '내 블로그에 오신 것을 환영합니다',
        'skills': '기술: Python, C++, 시스템 개발',
        'latest': '최신 글',
        'about': '내 소개',
        'login': '로그인/회원가입',
        'logout': '로그아웃',
        'admin': '관리자',
        'footer': '내 블로그',
        'back_home': '홈으로',
        'username': '사용자 이름',
        'phone': '전화번호/비밀번호',
        'login_register': '로그인/회원가입',
        'copyright': '내 블로그',
        'tip_title': '팁',
        'language_switch': '언어 전환',
        'theme': '테마',
        'light': '라이트',
        'dark': '다크',
        'delete_account': '계정 삭제',
        'confirm_delete_user': '정말 이 계정을 삭제하시겠습니까? 이 작업은 취소할 수 없습니다.',
        'new_post': '새 글 작성',
        'title_label': '제목',
        'content_label': '내용',
        'publish_post': '게시',
        'upload_images': '이미지 업로드 (최대 9장)',
        'choose_images': '이미지 선택',
        'only_images_allowed': '이미지 파일만 선택할 수 있습니다.',
        'max_images_limit': '최대 {n}장의 이미지만 업로드할 수 있습니다.',
        'edit_post': '글 수정',
        'delete_post': '글 삭제',
        'confirm_delete_post': '이 글을 삭제하시겠습니까?',
        'delete_success': '글이 삭제되었습니다!',
        'delete_fail': '글 삭제에 실패했습니다',
        'delete_error': '글 삭제 중 오류가 발생했습니다',
        'home': '홈',
        'games': '게임',
        'join': '가입하기',
        'settings': '설정',
        'contact': '연락처',
        'phone_label': '전화',
        'email_label': '이메일',
        'collapse': '접기',
        'downloads': '다운로드',
        'new_download': '다운로드 추가',
        'software_name': '소프트웨어 이름',
        'download_url': '다운로드 링크',
        'twofa_code': '인증 코드',
        'switch_account': '계정 전환',
        'change_avatar': '아바타 변경',
        'change_account_name': '계정명 변경',
        'batch_delete_users': '사용자 일괄 삭제',
        'avatar_updated': '아바타 업데이트 성공',
        'account_name_updated': '계정명 업데이트 성공',
        'back_downloads': '다운로드로 돌아가기',
        'breakout_game': '브레이크아웃',
        'memory_game': '기억력 게임',
        'sudoku_game': '스도쿠',
        'minesweeper_game': '지뢰찾기',
        'asteroids_game': '소행성',
        'pong_game': '퐁',
        'flappy_game': '플래피 버드',
        'game_description_breakout': '클래식 브레이크아웃 게임',
        'game_description_memory': '카드를 뒤집어 쌍을 찾는 기억력 게임',
        'game_description_2048': '숫자를 합쳐 2048에 도전하는 게임',
        'game_description_sudoku': '클래식 스도쿠 퍼즐',
        'game_description_minesweeper': '클래식 지뢰찾기 게임',
        'game_description_asteroids': '우주 슈팅 게임',
        'game_description_pong': '클래식 퐁 게임',
        'game_description_flappy': '클릭으로 새를 조종하여 장애물 피하기',
        'tank_game': '크레이지 탱크',
        'game_description_tank': '클래식 2D 탱크 배틀 게임, 플레이어 수를 선택하여 대전'
    },
    'ru': {
        'site_name': 'Мой блог',
        'welcome': 'Добро пожаловать в мой блог',
        'skills': 'Навыки: Python, C++, системная разработка',
        'latest': 'Последние статьи',
        'about': 'Обо мне',
        'login': 'Вход/Регистрация',
        'logout': 'Выйти',
        'admin': 'Админ',
        'footer': 'Мой блог',
        'back_home': 'На главную',
        'username': 'Имя пользователя',
        'phone': 'Телефон/Пароль',
        'login_register': 'Вход/Регистрация',
        'copyright': 'Мой блог',
        'tip_title': 'Совет',
        'language_switch': 'Смена языка',
        'theme': 'Тема',
        'light': 'Светлая',
        'dark': 'Тёмная',
        'delete_account': 'Удалить аккаунт',
        'confirm_delete_user': 'Вы уверены, что хотите удалить этот аккаунт? Это действие необратимо.',
        'new_post': 'Новая запись',
        'title_label': 'Заголовок',
        'content_label': 'Содержание',
        'publish_post': 'Опубликовать',
        'upload_images': 'Загрузка изображений (до 9)',
        'choose_images': 'Выбрать изображения',
        'only_images_allowed': 'Разрешены только файлы изображений.',
        'max_images_limit': 'Можно загрузить не более {n} изображений.',
        'edit_post': 'Редактировать запись',
        'delete_post': 'Удалить запись',
        'confirm_delete_post': 'Вы уверены, что хотите удалить эту запись?',
        'delete_success': 'Запись успешно удалена!',
        'delete_fail': 'Не удалось удалить запись',
        'delete_error': 'Произошла ошибка при удалении записи',
        'home': 'Главная',
        'games': 'Игры',
        'join': 'Присоединиться',
        'settings': 'Настройки',
        'contact': 'Контакты',
        'phone_label': 'Телефон',
        'email_label': 'Email',
        'collapse': 'Свернуть',
        'downloads': 'Загрузки',
        'new_download': 'Новая загрузка',
        'software_name': 'Название ПО',
        'download_url': 'Ссылка для загрузки',
        'twofa_code': 'Код',
        'switch_account': 'Сменить аккаунт',
        'change_avatar': 'Изменить аватар',
        'change_account_name': 'Изменить имя аккаунта',
        'batch_delete_users': 'Массовое удаление пользователей',
        'avatar_updated': 'Аватар успешно обновлен',
        'account_name_updated': 'Имя аккаунта успешно обновлено',
        'back_downloads': 'Назад к загрузкам',
        'breakout_game': 'Арканоид',
        'memory_game': 'Игра на память',
        'sudoku_game': 'Судоку',
        'minesweeper_game': 'Сапер',
        'asteroids_game': 'Астероиды',
        'pong_game': 'Понг',
        'flappy_game': 'Флэппи Берд',
        'game_description_breakout': 'Классическая игра Арканоид',
        'game_description_memory': 'Игра на память с картами',
        'game_description_2048': 'Игра слияния чисел до 2048',
        'game_description_sudoku': 'Классическая головоломка Судоку',
        'game_description_minesweeper': 'Классическая игра Сапер',
        'game_description_asteroids': 'Космическая стрелялка',
        'game_description_pong': 'Классическая игра Понг',
        'game_description_flappy': 'Управляйте птицей, избегая препятствий',
        'tank_game': 'Безумные Танки',
        'game_description_tank': 'Классическая 2D танковая битва, выберите количество игроков для сражения'
    },
    'es': {
        'site_name': 'Mi Blog',
        'welcome': 'Bienvenido a Mi Blog',
        'skills': 'Habilidades: Python, C++, Desarrollo de Sistemas',
        'latest': 'Últimas Publicaciones',
        'about': 'Sobre mí',
        'login': 'Iniciar sesión/Registrarse',
        'logout': 'Salir',
        'admin': 'Administrador',
        'footer': 'Mi Blog',
        'back_home': 'Volver al inicio',
        'username': 'Usuario',
        'phone': 'Teléfono/Contraseña',
        'login_register': 'Iniciar/Registrar',
        'copyright': 'Mi Blog',
        'tip_title': 'Consejo',
        'language_switch': 'Idioma',
        'theme': 'Tema',
        'light': 'Claro',
        'dark': 'Oscuro',
        'delete_account': 'Eliminar cuenta',
        'confirm_delete_user': '¿Seguro que desea eliminar la cuenta? ¡No se puede deshacer!',
        'new_post': 'Nueva publicación',
        'title_label': 'Título',
        'content_label': 'Contenido',
        'publish_post': 'Publicar',
        'upload_images': 'Subir imágenes (hasta 9)',
        'choose_images': 'Elegir imágenes',
        'only_images_allowed': 'Sólo se permiten imágenes.',
        'max_images_limit': 'Puede subir como máximo {n} imágenes.',
        'edit_post': 'Editar publicación',
        'delete_post': 'Eliminar publicación',
        'confirm_delete_post': '¿Seguro que desea eliminar esta publicación?',
        'delete_success': '¡Publicación eliminada!',
        'delete_fail': 'Error al eliminar',
        'delete_error': 'Se produjo un error al eliminar',
        'home': 'Inicio',
        'games': 'Juegos',
        'join': 'Únete',
        'settings': 'Ajustes',
        'contact': 'Contacto',
        'phone_label': 'Teléfono',
        'email_label': 'Correo',
        'collapse': 'Ocultar',
        'downloads': 'Descargas',
        'new_download': 'Nueva descarga',
        'software_name': 'Nombre del software',
        'download_url': 'URL de descarga',
        'twofa_code': 'Código',
        'switch_account': 'Cambiar cuenta',
        'change_avatar': 'Cambiar avatar',
        'change_account_name': 'Cambiar nombre de cuenta',
        'batch_delete_users': 'Eliminar usuarios en lote',
        'avatar_updated': 'Avatar actualizado exitosamente',
        'account_name_updated': 'Nombre de cuenta actualizado exitosamente',
        'back_downloads': 'Volver a descargas',
        'breakout_game': 'Breakout',
        'memory_game': 'Juego de Memoria',
        'sudoku_game': 'Sudoku',
        'minesweeper_game': 'Buscaminas',
        'asteroids_game': 'Asteroides',
        'pong_game': 'Pong',
        'flappy_game': 'Flappy Bird',
        'game_description_breakout': 'Juego clásico Breakout',
        'game_description_memory': 'Juego de memoria con cartas',
        'game_description_2048': 'Juego de fusión de números hasta 2048',
        'game_description_sudoku': 'Rompecabezas clásico de Sudoku',
        'game_description_minesweeper': 'Juego clásico de Buscaminas',
        'game_description_asteroids': 'Juego de disparos espaciales',
        'game_description_pong': 'Juego clásico de Pong',
        'game_description_flappy': 'Controla el pájaro, evita obstáculos',
        'tank_game': 'Tanques Locos',
        'game_description_tank': 'Juego clásico de batalla de tanques 2D, elige el número de jugadores para luchar'
    }
}

def get_lang():
    return session.get('lang', 'zh')

@app.route('/setlang/<lang>')
def setlang(lang):
    if lang in LANGUAGES:
        session['lang'] = lang
    return redirect(request.referrer or url_for('login'))

@app.before_request
def require_login():
    if request.endpoint in ['login', 'register', 'setlang', 'static']:
        return
    if 'user' not in session:
        return redirect(url_for('login'))

@app.route('/')
def index():
    posts = []
    # 将博客文章添加到列表中，并赋予ID
    for i, post in enumerate(blog_posts):
        posts.append({'id': i, 'title': post['title'], 'content': post['content'], 'image_urls': post.get('image_urls', [])})
    # 添加小技巧作为最后一个"post"，赋予特殊ID（例如 -1）
    # 确保小技巧也有一个id，即使它不会跳转到详细页面

    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    
    # 准备主页展示的文章列表，只包含标题、部分内容和ID
    display_posts = []
    for post in posts: # 这里的 post 应该已经包含 id 了
        display_content = post['content']
        if len(display_content) > 300: # 截断长度可以调整
            display_content = display_content[:300] + '...'
        # 确保将id也添加到 display_posts 中
        display_posts.append({'id': post['id'], 'title': post['title'], 'content': display_content, 'image_urls': post.get('image_urls', [])})

    return render_template('index.html', posts=display_posts, user=user, lang=lang, languages=LANGUAGES, year=year, text=text, CODE_TIPS=CODE_TIPS)

@app.route('/about')
def about():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('about.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/games')
def games():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('games.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/snake')
def game_snake():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_snake.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/tetris')
def game_tetris():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_tetris.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/pacman')
def game_pacman():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_pacman.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/breakout')
def game_breakout():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_breakout.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/memory')
def game_memory():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_memory.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/2048')
def game_2048():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_2048.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/sudoku')
def game_sudoku():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_sudoku.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/minesweeper')
def game_minesweeper():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_minesweeper.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/asteroids')
def game_asteroids():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_asteroids.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/pong')
def game_pong():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_pong.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/flappy')
def game_flappy():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_flappy.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/game/tank')
def game_tank():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('game_tank.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/join')
def join():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('join.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/downloads')
def downloads():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    return render_template('downloads.html', downloads=downloads_store, user=user, lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/admin/new_download', methods=['GET', 'POST'])
def new_download():
    if session.get('user') != 'admin':
        flash('只有管理员才能新增下载')
        return redirect(url_for('downloads'))
    lang = get_lang()
    text = LANG_TEXT[lang]
    if request.method == 'POST':
        name = request.form.get('name')
        url_value = request.form.get('url')
        if name and url_value:
            downloads_store.append({'name': name, 'url': url_value})
            save_downloads()
            return redirect(url_for('downloads'))
        flash('名称与链接不能为空')
    return render_template('new_download.html', lang=lang, languages=LANGUAGES, text=text)

@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = get_lang()
    text = LANG_TEXT[lang]
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        result = register_user(username, password)
        if result == '':
            flash(text['register_success'])
            return redirect(url_for('login'))
        else:
            flash(result)
    return render_template('register.html', lang=lang, languages=LANGUAGES, text=text)

@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = get_lang()
    text = LANG_TEXT[lang]
    need2fa = request.args.get('need2fa') == '1'
    if request.method == 'POST':
        twofa = request.form.get('twofa')
        if twofa:
            if session.get('2fa_code') and twofa == session.get('2fa_code') and session.get('2fa_user'):
                session['user'] = session.pop('2fa_user')
                session.pop('2fa_code', None)
                flash('管理员登录成功！')
                return redirect(url_for('index'))
            else:
                flash('验证码错误')
                return redirect(url_for('login', need2fa=1))

        username = request.form.get('username')
        password = request.form.get('phone')
        # 游客身份登录
        if username == '游客' and (not password or password == ''):
            session['user'] = '游客'
            flash('以游客身份登录成功！')
            return redirect(url_for('index'))

        if verify_user(username, password):
            if get_role(username) == 'admin':
                code = ''.join(random.choices(string.digits, k=6))
                session['2fa_code'] = code
                session['2fa_user'] = 'admin'
                print(f"[2FA] Admin verification code: {code}")
                flash('管理员登录需要验证码，请输入验证码')
                return redirect(url_for('login', need2fa=1))
            else:
                session['user'] = username
                flash(text['login_register'] + '成功！')
                return redirect(url_for('index'))
        else:
            flash(text['phone'] + '错误')
    return render_template('login.html', lang=lang, languages=LANGUAGES, text=text, need2fa=need2fa)

@app.route('/logout')
def logout():
    session.pop('user', None)
    lang = get_lang()
    text = LANG_TEXT[lang]
    flash(text['logout'] + '成功')
    return redirect(url_for('login'))

@app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    # 检查是否是管理员
    if session.get('user') != 'admin':
        return jsonify({'success': False, 'message': '只有管理员才能删除文章'}), 403

    # 检查文章ID是否有效并删除
    if 0 <= post_id < len(blog_posts):
        del blog_posts[post_id]
        save_posts() # 保存文章
        # 注意：这里删除后会改变后续文章的ID，如果频繁删除可能需要更复杂的ID管理（如UUID）
        return jsonify({'success': True, 'message': '文章删除成功'}), 200
    else:
        return jsonify({'success': False, 'message': '文章未找到'}), 404

@app.route('/admin/delete_posts', methods=['POST'])
def delete_posts():
    if session.get('user') != 'admin':
        return jsonify({'success': False, 'message': '只有管理员才能删除文章'}), 403
    try:
        ids = request.json.get('ids', []) if request.is_json else request.form.getlist('ids[]')
        ids = sorted(set(int(i) for i in ids if str(i).isdigit()), reverse=True)
        deleted = []
        for pid in ids:
            if 0 <= pid < len(blog_posts):
                del blog_posts[pid]
                deleted.append(pid)
        if deleted:
            save_posts()
        return jsonify({'success': True, 'deleted': deleted})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/settings')
def settings():
    user = session.get('user')
    lang = get_lang()
    year = datetime.datetime.now().year
    text = LANG_TEXT[lang]
    admin_user_list = []
    if user == 'admin':
        try:
            admin_user_list = [u.get('display') for u in users_store.values() if u.get('role') != 'admin']
        except Exception:
            admin_user_list = []
    return render_template('settings.html', user=user, lang=lang, languages=LANGUAGES, year=year, text=text, users_list=admin_user_list)

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user = session.get('user')
    if user and user != 'admin':
        delete_user_record(user)
    session.pop('user', None)
    return '', 204

@app.route('/admin/delete_user/<username>', methods=['POST'])
def admin_delete_user(username):
    if session.get('user') != 'admin':
        return jsonify({'success': False, 'message': '只有管理员才能删除用户'}), 403
    if username == 'admin':
        return jsonify({'success': False, 'message': '不能删除管理员'}), 400
    if delete_user_record(username):
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': '用户不存在'}), 404

@app.route('/admin/batch-delete-users', methods=['GET', 'POST'])
def batch_delete_users():
    if session.get('user') != 'admin':
        flash('只有管理员才能访问此页面')
        return redirect(url_for('index'))
    
    lang = get_lang()
    text = LANG_TEXT[lang]
    year = datetime.datetime.now().year
    
    if request.method == 'POST':
        try:
            usernames = request.json.get('usernames', []) if request.is_json else request.form.getlist('usernames[]')
            deleted = []
            for username in usernames:
                if username != 'admin' and delete_user_record(username):
                    deleted.append(username)
            return jsonify({'success': True, 'deleted': deleted})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    # GET request - show the batch delete interface
    user_list = [u.get('display') for u in users_store.values() if u.get('role') != 'admin']
    return render_template('batch_delete_users.html', users_list=user_list, user=session.get('user'), lang=lang, languages=LANGUAGES, year=year, text=text)

@app.route('/tip')
def get_tip():
    import random
    last_tip = request.args.get('last', '')
    available_tips = [tip for tip in CODE_TIPS if tip != last_tip]
    tip = random.choice(available_tips) if available_tips else random.choice(CODE_TIPS)
    return {'tip': tip}

blog_posts = [] # 用于存储博客文章

# 文件路径用于存储文章数据（使用绝对路径，避免工作目录变更导致找不到文件）
POSTS_FILE = os.path.join(BASE_DIR, 'posts.json')

# 图片上传目录（文件系统绝对路径）与 URL 前缀分离
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
UPLOAD_URL_PREFIX = '/static/uploads'

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 加载文章数据
def load_posts():
    global blog_posts
    try:
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            blog_posts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或解析失败，则初始化为空列表
        blog_posts = []

# 保存文章数据
def save_posts():
    try:
        with open(POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(blog_posts, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving posts: {e}") # 打印错误信息，但不阻止程序运行

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    lang = get_lang()
    text = LANG_TEXT[lang]
    post = None
    if 0 <= post_id < len(blog_posts):
        post = blog_posts[post_id]
    
    if post:
        user = session.get('user')
        return render_template('post_detail.html', post=post, post_id=post_id, user=user, lang=lang, languages=LANGUAGES, text=text)
    else:
        flash('文章未找到')
        return redirect(url_for('index'))

@app.route('/admin/new_post', methods=['GET', 'POST'])
def new_post():
    # 检查是否是管理员
    if session.get('user') != 'admin':
        flash('只有管理员才能创建文章')
        return redirect(url_for('index'))

    lang = get_lang()
    text = LANG_TEXT[lang]

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # 处理图片上传
        uploaded_image_urls = []
        files = request.files.getlist('files[]')
        print(f"Received {len(files)} files for new post.") # Log number of received files
        for file in files:
                if file.filename == '':
                    print("Skipping file with empty filename for new post.") # Log empty filename
                    continue
                try:
                    if file:
                        filename = secure_filename(file.filename)
                    # 使用绝对文件系统路径保存
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    print(f"Attempting to save file '{filename}' to: {filepath}") # Add print statement before save
                    try: # Wrap file.save in a try-except block
                        file.save(filepath)
                        uploaded_image_urls.append(f"{UPLOAD_URL_PREFIX}/{filename}")
                        print(f"Uploaded image saved to: {filepath}, URL: {uploaded_image_urls[-1]}") # Log successful upload path and URL
                    except Exception as save_error: # Catch exceptions from save
                        print(f"Error saving file {filename}: {save_error}") # Log save errors
                        # Decide how to handle save errors - maybe continue with other files or abort
                        continue # For now, just log and continue with other files
                except Exception as e:
                    print(f"Error uploading file {file.filename} for new post: {e}") # Log upload errors

        if title and content:
            try:
                # 存储文章数据，包含图片路径列表
                blog_posts.append({'title': title, 'content': content, 'image_urls': uploaded_image_urls}) # 使用 image_urls 存储列表
                print(f"New post added with image URLs: {uploaded_image_urls}") # Log image URLs for new post
                save_posts() # 保存文章
                flash('文章发布成功！')
                # 返回JSON响应给前端，包含重定向URL
                return jsonify({'success': True, 'message': '文章发布成功！', 'redirect_url': url_for('index')})
            except Exception as e:
                print(f"Error updating post data or saving: {e}") # Log data update/save errors
                return jsonify({'success': False, 'message': f'服务器内部错误：{e}'}), 500 # 返回更详细的错误信息
        else:
            flash('标题和内容不能为空')
            # 返回JSON响应给前端
            return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

    return render_template('new_post.html', lang=lang, languages=LANGUAGES, text=text)

# 图片上传路由
@app.route('/admin/upload_image', methods=['POST'])
def upload_image():
    # 检查是否是管理员
    if session.get('user') != 'admin':
        return jsonify({'success': False, 'message': '只有管理员才能上传图片'}), 403

    if 'files[]' not in request.files:
        return jsonify({'success': False, 'message': '没有文件部分'}), 400

    files = request.files.getlist('files[]')
    uploaded_files = []

    for file in files:
        if file.filename == '':
            continue
        if file:
            filename = secure_filename(file.filename)
            # 使用绝对文件系统路径保存
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            print(f"Attempting to save file '{filename}' to: {filepath}") # Add print statement before save
            try: # Wrap file.save in a try-except block
                file.save(filepath)
                # 返回可直接用于浏览器的 URL
                uploaded_files.append(f"{UPLOAD_URL_PREFIX}/{filename}")
            except Exception as save_error: # Catch exceptions from save
                print(f"Error saving file {filename}: {save_error}") # Log save errors
                # Decide how to handle save errors - maybe continue with other files or abort
                continue # For now, just log and continue with other files

    return jsonify({'success': True, 'message': '图片上传成功', 'files': uploaded_files})

# 管理员编辑文章路由
@app.route('/admin/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    # 检查是否是管理员
    if session.get('user') != 'admin':
        flash('只有管理员才能编辑文章')
        return redirect(url_for('index'))

    lang = get_lang()
    text = LANG_TEXT[lang]

    # 检查文章ID是否有效
    if not (0 <= post_id < len(blog_posts)):
        flash('文章未找到')
        return redirect(url_for('index'))

    post = blog_posts[post_id]

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        # 处理图片的更新
        uploaded_image_urls = []

        # 获取需要删除的旧图片列表
        images_to_delete = request.form.getlist('images_to_delete[]')
        print(f"Images to delete: {images_to_delete}") # Log images to delete
        for image_url in images_to_delete:
            # 构建完整的图片文件路径并安全删除
            # 确保只删除 UPLOAD_FOLDER 下的文件
            try:
                filename = os.path.basename(image_url)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                # 进一步安全检查：确保路径在 UPLOAD_FOLDER 内
                if os.path.commonprefix([os.path.realpath(filepath), os.path.realpath(UPLOAD_FOLDER)]) == os.path.realpath(UPLOAD_FOLDER):
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"Deleted image: {filepath}") # Log successful deletion
                    else:
                        print(f"Attempted to delete non-existent image: {filepath}") # Log if file not found
                else:
                    print(f"Attempted to delete file outside UPLOAD_FOLDER: {filepath}") # Log potential security issue
            except Exception as e:
                print(f"Error deleting image {image_url}: {e}") # Log deletion errors

        # 处理上传的新图片
        if 'new_files[]' in request.files:
            files = request.files.getlist('new_files[]')
            print(f"Received {len(files)} new files.") # Log number of received files
            for file in files:
                if file.filename == '':
                    print("Skipping file with empty filename.") # Log empty filename
                    continue
                try:
                    if file:
                        filename = secure_filename(file.filename)
                        # 使用绝对文件系统路径保存
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        print(f"Attempting to save new file '{filename}' to: {filepath}") # Add print statement before save
                        try: # Wrap file.save in a try-except block
                            file.save(filepath)
                            uploaded_image_urls.append(f"{UPLOAD_URL_PREFIX}/{filename}")
                            print(f"Uploaded new image saved to: {filepath}, URL: {uploaded_image_urls[-1]}") # Log successful upload path and URL
                        except Exception as save_error: # Catch exceptions from save
                            print(f"Error saving new file {filename}: {save_error}") # Log save errors
                            # Decide how to handle save errors - maybe continue with other files or abort
                            continue # For now, just log and continue with other files
                except Exception as e:
                    print(f"Error uploading file {file.filename}: {e}") # Log upload errors

        # 构建新的图片URL列表：保留未删除的旧图片 + 新上传的图片
        # 从 request.form.getlist('existing_image_urls[]') 获取未删除的旧图片列表
        remaining_existing_urls = request.form.getlist('existing_image_urls[]')
        print(f"Remaining existing image URLs: {remaining_existing_urls}") # Log remaining existing URLs
        print(f"Uploaded image URLs: {uploaded_image_urls}") # Log uploaded URLs
        new_image_urls = remaining_existing_urls + uploaded_image_urls
        print(f"Final image URLs for post: {new_image_urls}") # Log final image URLs

        if title and content:
            try:
                # 更新文章数据，包括新的图片URL列表
                blog_posts[post_id]['title'] = title
                blog_posts[post_id]['content'] = content
                blog_posts[post_id]['image_urls'] = new_image_urls
                save_posts() # 保存文章
                flash('文章更新成功！')
                # 返回JSON响应给前端，包含重定向URL
                return jsonify({'success': True, 'message': '文章更新成功！', 'redirect_url': url_for('post_detail', post_id=post_id)})
            except Exception as e:
                print(f"Error updating post data or saving: {e}") # Log data update/save errors
                return jsonify({'success': False, 'message': f'服务器内部错误：{e}'}), 500 # 返回更详细的错误信息
        else:
            flash('标题和内容不能为空')
            # 返回JSON响应给前端
            return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

    # GET 请求时，渲染编辑页面
    return render_template('edit_post.html', post=post, post_id=post_id, lang=lang, languages=LANGUAGES, text=text)

load_posts() # 模块导入时加载文章，适配 WSGI 部署
load_users()
ensure_admin_exists()
load_downloads()
if __name__ == '__main__':
    app.run(debug=True)
