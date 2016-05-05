var app=angular.module('ita',['angularUtils.directives.dirPagination']);

app.controller("DocumentController",['$scope','$http',function($scope,$http){
	$scope.message="Hello World";

	$http.get("http://127.0.0.1:5000/docs").then(function(response){
			$scope.docs=response.data;
			console.log($scope.docs);
	});	

	$scope.delete=function(index,id){

		// alert(id);
		// alert(index);
		$http.get("http://127.0.0.1:5000/delete/"+id).then(function(response){
			var resp=response.data;
			if(response.status==200){
				alert("successfully deleted");
			}
		});

	}



}]);


app.controller("SearchController",['$scope','$http',function($scope,$http){
	$scope.message="Hello World";

	$scope.submit=function(){
		// alert("search click");
		var data=JSON.stringify({
			'filter':$scope.filter,
			'name':$scope.find
		});

		// $http.get("http://127.0.0.1:5000/search/"+$scope.filter+"/"+$scope.find).success(function(data,error){
		// 	$scope.docs=data;
		// });
		$http.post("http://127.0.0.1:5000/s",data).success(function(data,error){
			$scope.docs=data;
		});

	}

	


}]);

app.controller("UploadController",['$scope',function($scope){
	
}]);