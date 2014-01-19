CHANGELOG
---------

### 19 Jan 2013

* Framework
	* folders refactored
		* `lib` > `assets`
		* `lib/img` > `static/img`
		* `sources/vendors` > `lib`

	* assets manager  
		We don't use anymore preprocessor but flask-assets.  
		Now, you have to register assets in `assets.yaml`. Files will be processed and merged as defined.
	* clevercss updated
