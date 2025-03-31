class Exercise(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Categoría")
    equipment = models.ForeignKey('Equipment', on_delete=models.SET_NULL, null=True, verbose_name="Equipamiento")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name="Dificultad")
    image = models.ImageField(upload_to='exercises/', null=True, blank=True, verbose_name="Imagen")
    youtube_url = models.URLField(max_length=200, null=True, blank=True, verbose_name="URL de YouTube")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ['name']

    def __str__(self):
        return self.name 