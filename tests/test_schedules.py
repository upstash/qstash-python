from upstash_qstash import QStash


def test_schedule_lifecycle(qstash: QStash) -> None:
    sched_id = qstash.schedule.create_json(
        cron="* * * * *",
        destination="https://example.com",
        body={"ex_key": "ex_value"},
    )

    assert len(sched_id) > 0

    res = qstash.schedule.get(sched_id)
    assert res.schedule_id == sched_id
    assert res.cron == "* * * * *"

    list_res = qstash.schedule.list()
    assert any(s.schedule_id == sched_id for s in list_res)

    qstash.schedule.delete(sched_id)

    list_res = qstash.schedule.list()
    assert not any(s.schedule_id == sched_id for s in list_res)
