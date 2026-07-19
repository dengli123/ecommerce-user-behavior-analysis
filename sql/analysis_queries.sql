-- 电商用户行为多维分析 SQL（可在 SQLite / MySQL 中执行）
-- 表名：user_behavior
-- 字段：user_id, item_id, category, behavior, timestamp, price, province, date, hour

-- 1. 行为漏斗：浏览 -> 加购 -> 收藏 -> 购买
SELECT
    behavior,
    COUNT(*) AS event_cnt,
    COUNT(DISTINCT user_id) AS user_cnt
FROM user_behavior
GROUP BY behavior
ORDER BY event_cnt DESC;

-- 2. 日活跃用户（DAU）
SELECT
    date,
    COUNT(DISTINCT user_id) AS dau
FROM user_behavior
GROUP BY date
ORDER BY date;

-- 3. 复购率（购买次数 >= 2 的用户占比）
WITH buy_users AS (
    SELECT
        user_id,
        COUNT(*) AS buy_cnt
    FROM user_behavior
    WHERE behavior = 'buy'
    GROUP BY user_id
)
SELECT
    COUNT(*) AS buy_user_cnt,
    SUM(CASE WHEN buy_cnt >= 2 THEN 1 ELSE 0 END) AS repurchase_user_cnt,
    ROUND(1.0 * SUM(CASE WHEN buy_cnt >= 2 THEN 1 ELSE 0 END) / COUNT(*), 4) AS repurchase_rate
FROM buy_users;

-- 4. 品类消费偏好（GMV + 购买人数）
SELECT
    category,
    COUNT(*) AS buy_orders,
    COUNT(DISTINCT user_id) AS buy_users,
    ROUND(SUM(price), 2) AS gmv,
    ROUND(AVG(price), 2) AS avg_price
FROM user_behavior
WHERE behavior = 'buy'
GROUP BY category
ORDER BY gmv DESC;

-- 5. 省份 GMV Top10
SELECT
    province,
    ROUND(SUM(price), 2) AS gmv,
    COUNT(DISTINCT user_id) AS buyers
FROM user_behavior
WHERE behavior = 'buy'
GROUP BY province
ORDER BY gmv DESC
LIMIT 10;

-- 6. 小时活跃分布
SELECT
    hour,
    COUNT(*) AS event_cnt,
    COUNT(DISTINCT user_id) AS user_cnt
FROM user_behavior
GROUP BY hour
ORDER BY hour;

-- 7. 转化率（用户级）：浏览用户中最终购买的比例
WITH users AS (
    SELECT
        user_id,
        MAX(CASE WHEN behavior = 'pv' THEN 1 ELSE 0 END) AS has_pv,
        MAX(CASE WHEN behavior = 'cart' THEN 1 ELSE 0 END) AS has_cart,
        MAX(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) AS has_buy
    FROM user_behavior
    GROUP BY user_id
)
SELECT
    SUM(has_pv) AS pv_users,
    SUM(has_cart) AS cart_users,
    SUM(has_buy) AS buy_users,
    ROUND(1.0 * SUM(has_buy) / NULLIF(SUM(has_pv), 0), 4) AS pv_to_buy_rate,
    ROUND(1.0 * SUM(has_buy) / NULLIF(SUM(has_cart), 0), 4) AS cart_to_buy_rate
FROM users;
