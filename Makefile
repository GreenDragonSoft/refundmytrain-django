.PHONY: test
test:
	./manage.py test -v 3 --failfast

.PHONY: load
load:
	./manage.py loaddata refundmytrain/fixtures/paul.json
	./manage.py import_operating_companies db/operating_companies.json
	./manage.py import_corpus db/network_rail_corpus.json
	./manage.py import_naptan db/naptan_rail_locations.json
	./manage.py build_corpus_naptan_links
	./manage.py cron_update_data

.PHONY: runserver
runserver:
	./manage.py runserver 0.0.0.0:8001
