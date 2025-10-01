# LookHub Поэтапный План Деплоя

## 📋 Обзор
Этот документ описывает поэтапный процесс деплоя приложения LookHub в продакшн среду.

## 🎯 Цели
- Безопасный и надежный деплой
- Минимальное время простоя
- Возможность быстрого отката
- Мониторинг и логирование
- Резервное копирование

---

## 🚀 Этап 1: Подготовка Сервера

### 1.1 Требования к серверу
- **OS**: Ubuntu 22.04 LTS+ или CentOS 8+
- **RAM**: Минимум 4GB, рекомендуется 8GB+
- **CPU**: 2+ ядра
- **Диск**: 50GB+ SSD
- **Сеть**: Статический IP адрес

### 1.2 Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

### 1.3 Усиление безопасности
```bash
# Запуск скрипта усиления безопасности
sudo bash security/harden-server.sh

# Настройка SSH ключей
ssh-keygen -t ed25519 4096 -C "your-email@example.com"
```

---

## 🔧 Этап 2: Конфигурация Окружения

### 2.1 Создание .env файлов
```bash
# Создание .env файла на основе примера
cp env.example .env.prod

# Редактирование переменных окружения
nano .env.prod
```

### 2.2 Настройка переменных окружения
**Обязательные переменные для LookHubWeb/.env:**
```env
# Основной домен для продакшна
DOMAIN=example.com

# Email для Let's Encrypt
SSL_EMAIL=example@example.com

# База данных
POSTGRES_DB=lookhub
POSTGRES_USER=lookhubweb
POSTGRES_PASSWORD=your_strong_password

# Безопасность
ADMIN_JWT_SECRET=your_jwt_secret_key
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_super_secret_user_password

API_KEY=your_super_secret_api_key

#Instagram credentials
INSTAGRAM_LOGIN=your_instagram_login
INSTAGRAM_PASSWORD=your_instagram_password

#Telegram credentials
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=-your_telegram_chat_id
```


## 🐳 Этап 3: Деплой Приложения

### 3.1 Первоначальный деплой
```bash
# Клонирование проекта (если не на сервере)
git clone <repository-url>
cd LookHub

# Сборка и запуск продакшн контейнеров
docker-compose -f docker-compose.prod.yaml build --no-cache
docker-compose -f docker-compose.prod.yaml up -d

# Проверка статуса сервисов
docker-compose -f docker-compose.prod.yaml ps
```

### 3.2 Проверка работоспособности
```bash
# Проверка логов
docker-compose -f docker-compose.prod.yaml logs -f

# Проверка health check
curl -f http://localhost/health

# Проверка базы данных
docker exec lookhub-db pg_isready -U lookhubweb -d lookhub
```

---

## 🔒 Этап 4: Настройка SSL

### 4.1 Получение SSL сертификата
```bash
# Для продакшена (Let's Encrypt)
sudo bash security/setup-ssl.sh your-domain.com admin@your-domain.com

# Для разработки (самоподписанный)
sudo bash security/setup-ssl.sh localhost admin@localhost dev
```

### 4.2 Обновление конфигурации Nginx
```bash
# Обновление домена в конфигурации
sed -i 's/your-domain.com/your-actual-domain.com/g' nginx.prod.conf

# Перезапуск Nginx
docker-compose -f docker-compose.prod.yaml restart nginx
```

---

## 📊 Этап 5: Мониторинг

### 5.1 Запуск системы мониторинга
```bash
# Запуск Prometheus, Grafana и Loki
cd monitoring
docker-compose -f docker-compose.monitoring.yaml up -d

# Проверка доступности
curl -f http://localhost:9090  # Prometheus
curl -f http://localhost:3000  # Grafana
```

### 5.2 Настройка Grafana
1. Открыть http://your-domain.com:3000
2. Логин: admin, Пароль: admin123
3. Импортировать дашборды из `monitoring/grafana/dashboards/`

---

## 💾 Этап 6: Резервное Копирование

### 6.1 Настройка автоматических бэкапов
```bash
# Создание директории для бэкапов
mkdir -p backups

# Тестовый бэкап
./backup.bat

# Настройка cron для автоматических бэкапов
crontab -e
# Добавить: 0 2 * * * /path/to/backup.bat
```

### 6.2 Тестирование восстановления
```bash
# Тестирование восстановления из бэкапа
./restore.bat
```

---

## 🔄 Этап 7: Обновление Приложения

### 7.1 Процедура обновления
```bash
# 1. Создание бэкапа
./backup.bat

# 2. Остановка сервисов
docker-compose -f docker-compose.prod.yaml down

# 3. Обновление кода
git pull origin main

# 4. Пересборка образов
docker-compose -f docker-compose.prod.yaml build --no-cache

# 5. Запуск обновленных сервисов
docker-compose -f docker-compose.prod.yaml up -d

# 6. Проверка работоспособности
curl -f http://localhost/health
```

### 7.2 Откат при проблемах
```bash
# Откат к предыдущей версии
./restore.bat
```

---

## 📋 Чек-лист Деплоя

### ✅ Подготовка
- [ ] Сервер подготовлен и защищен
- [ ] Docker и Docker Compose установлены
- [ ] .env файлы созданы и настроены
- [ ] SSL сертификаты получены
- [ ] Домен настроен

### ✅ Деплой
- [ ] Приложение развернуто
- [ ] База данных инициализирована
- [ ] Все сервисы запущены
- [ ] Health checks проходят
- [ ] SSL работает

### ✅ Мониторинг
- [ ] Prometheus запущен
- [ ] Grafana настроена
- [ ] Логи собираются
- [ ] Алерты настроены

### ✅ Безопасность
- [ ] Firewall настроен
- [ ] Fail2ban активен
- [ ] SSH защищен
- [ ] SSL настроен

### ✅ Резервное копирование
- [ ] Бэкапы создаются
- [ ] Восстановление протестировано
- [ ] Автоматизация настроена

---

## 🚨 Процедуры в Случае Проблем

### Проблемы с базой данных
```bash
# Проверка статуса
docker exec lookhub-db pg_isready -U lookhubweb -d lookhub

# Просмотр логов
docker logs lookhub-db

# Восстановление из бэкапа
./restore.bat
```

### Проблемы с приложением
```bash
# Просмотр логов
docker-compose -f docker-compose.prod.yaml logs lookhub-web

# Перезапуск сервиса
docker-compose -f docker-compose.prod.yaml restart lookhub-web
```

### Проблемы с Nginx
```bash
# Проверка конфигурации
docker exec lookhub-nginx nginx -t

# Перезапуск Nginx
docker-compose -f docker-compose.prod.yaml restart nginx
```

---

## 📞 Контакты и Поддержка

### Логи и мониторинг
- **Приложение**: http://your-domain.com
- **Админ панель**: http://your-domain.com/admin
- **Grafana**: http://your-domain.com:3000
- **Prometheus**: http://your-domain.com:9090
- **Flower**: http://your-domain.com/flower

### Полезные команды
```bash
# Статус всех сервисов
docker-compose -f docker-compose.prod.yaml ps

# Логи всех сервисов
docker-compose -f docker-compose.prod.yaml logs -f

# Статистика ресурсов
docker stats

# Проверка места на диске
df -h

# Проверка памяти
free -h
```

---

## 📝 Примечания

1. **Безопасность**: Регулярно обновляйте пароли и ключи
2. **Мониторинг**: Следите за логами и метриками
3. **Бэкапы**: Проверяйте целостность бэкапов
4. **Обновления**: Тестируйте обновления на staging среде
5. **Документация**: Ведите журнал изменений

---

*Последнее обновление: $(date)*

