package main

import (
	"github.com/gin-gonic/gin"
	"github.com/yourusername/metrics-api-service/controllers"
)

func main() {
	router := gin.Default()
	router.GET("/health", controllers.GetHealth)
	router.Run()
}
