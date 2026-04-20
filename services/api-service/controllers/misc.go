package controllers

import (
	"github.com/gin-gonic/gin"
)

func GetHealth(c *gin.Context) {
	c.JSON(
		200,
		gin.H{"message": "This route was pinged and works!"})
}
