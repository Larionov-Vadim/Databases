larionov_api
=================
#####Учебный проект [tech-mail.ru](https://tech-mail.ru/) по курсу СУБД
#####Выполнил студент: Larionov Vadim, git: [Larionov-Vadim](https://github.com/Larionov-Vadim)

Суть задания заключается в реализации API к базе данных проекта «Форумы» по документации к, собственно, этому API, т.е. эдакий реверс-инжиниринг.
Таким образом, на входе:

* документация к API

На выходе:
* поднятый и настроенный MySQL
* БД где будет хранится информация об основных сущностях системы
* вэб-сервер, который будет отвечать на внешние запросы, обращаясь к БД

После написания API правильность реализации будет проверяться с помощью автоматического функционального тестирования.
Методика тестирования:
* запускается скрипт на python, который будет проводить тестирование
* он опрашивает все методы, определенные в API, по шаблону http://{{student_ip}}/db/api//{{entity}}/{{method}}/ с заранее заданными\случайными параметрами, корректными относительно документации (в POST-запросах передается json, GET - как обычно)
* ответы вашей системы сравниваются с эталонами
* если код http ответа не 200, то тест считается проваленным
* если в ответе не хватает каких-то полей или значение каких-то полей не совпадает, то тест считается проваленным
* если нет ни одного неправильного ответа, то тест считается пройденным
* результат тест отправляется вам на почту

##FAQ
1. Что нужно ответить, если создаваемый объект\связь уже существует?
  - Нужно ответить этим уже созданным объектом для всех сущностей, кроме юзера. В случае юзера вернуть ошибку (см. п. 4 и 2)

2. Что такое code в ответах на запросы?
  - Код возврата: 
    * 0 — ОК, 
    * 1 — запрашиваемый объект не найден,
    * 2 — невалидный запрос (например, не парсится json),
    * 3 — некорректный запрос (семантически),
    * 4 — неизвестная ошибка.
    * 5 — такой юзер уже существует

3. Юзер может несколько раз голосовать за один и тот же пост или тред?
  - Да
4. Что отвечать в случае ошибки?
  - {"code": *code*, "response": *error message*}
5. Что делать при удалении треда\поста? 
  - Сущность помечается, как isDeleted. Для поста помечается только он сам, для треда - все его внутренности. При этом удаленные сущности не учитываются при подсчете, например, количества постов в треде, но передаются в теле ответа.
6. Уникален ли username?
  - Нет, уникален email
7. Уникален ли name у Forum?
  - да, как и shortname
8. Что такое related user у Forums.details?
  - Показать полную информацию о создателе форума (вместо просто его email-а)
9. Что за типы сортировок для постов ['flat', 'tree', 'parent_tree']?
  - Есть три вида сортировок с пагинацией, они оказываются очень интересными:
    * по дате (flat), комментарии выводятся простым списком по дате,
    * древовидный (tree), комментарии выводятся отсортированные в дереве по N штук,
    * древовидные с пагинацией по родительским (parent_tree), на странице N родительских комментов и все комментарии прикрепленные к ним, в древвидном отображение,

  У всех вариантов есть asc и desc сортировки.
  Подробнее тут: https://tech-mail.ru/blog/database/2027.html
10. Как запускать тесты локально?
  - python func_test.py -l --address=127.0.0.1:5000 .  Другие опции смотри по ключу -h 
11. Как провести нагрузочное тестирование локально?
  - python perf_test.py  -l --address=127.0.0.1:5000 заполнит вашу базу согласно опциям из конфига (см. test.conf) и создаст файлик me_httperf_scenario. Его нужно подавать на вход httperf так: httperf --hog --client=0/1 --server=127.0.0.1 --port=5000 --uri=/ --send-buffer=4096 --recv-buffer=16384  --add-header='Content-Type:application/json\n' --wsesslog=100,0.000,me_httperf_scenario . Запускать на 5 минут, смотреть на Reply rate -> avg 

#API Documentation

##Общие
* [clear](./technopark-db-api/doc/clear.md)

##Forum
* [create](./technopark-db-api/doc/forum/create.md)
* [details](./technopark-db-api/doc/forum/details.md)
* [listPosts](./technopark-db-api/doc/forum/listPosts.md)
* [listThreads](./technopark-db-api/doc/forum/listThreads.md)
* [listUsers](./technopark-db-api/doc/forum/listUsers.md)

##Post
* [create](./technopark-db-api/doc/post/create.md)
* [details](./technopark-db-api/doc/post/details.md)
* [list](./technopark-db-api/doc/post/list.md)
* [remove](./technopark-db-api/doc/post/remove.md)
* [restore](./technopark-db-api/doc/post/restore.md)
* [update](./technopark-db-api/doc/post/update.md)
* [vote](./technopark-db-api/doc/post/vote.md)

##User
* [create](./technopark-db-api/doc/user/create.md)
* [details](./technopark-db-api/doc/user/details.md)
* [follow](./technopark-db-api/doc/user/follow.md)
* [listFollowers](./technopark-db-api/doc/user/listFollowers.md)
* [listFollowing](./technopark-db-api/doc/user/listFollowing.md)
* [listPosts](./technopark-db-api/doc/user/listPosts.md)
* [unfollow](./technopark-db-api/doc/user/unfollow.md)
* [updateProfile](./technopark-db-api/doc/user/updateProfile.md)

##Thread
* [close](./technopark-db-api/doc/thread/close.md)
* [create](./technopark-db-api/doc/thread/create.md)
* [details](./technopark-db-api/doc/thread/details.md)
* [list](./technopark-db-api/doc/thread/list.md)
* [listPosts](./technopark-db-api/doc/thread/listPosts.md)
* [open](./technopark-db-api/doc/thread/open.md)
* [remove](./technopark-db-api/doc/thread/remove.md)
* [restore](./technopark-db-api/doc/thread/restore.md)
* [subscribe](./technopark-db-api/doc/thread/subscribe.md)
* [unsubscribe](./technopark-db-api/doc/thread/unsubscribe.md)
* [update](./technopark-db-api/doc/thread/update.md)
* [vote](./technopark-db-api/doc/thread/vote.md)

