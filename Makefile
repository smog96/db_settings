pub: code patch build publish
pub_minor: code minor build publish
pub_major: code major build publish

build:
	poetry build

code:
	poetry run black db_settings
	poetry run isort db_settings

patch:
	poetry version patch

minor:
	poetry version minor

major:
	poetry version major

publish:
	poetry publish -r antiddos
	poetry publish -r wb_nexus