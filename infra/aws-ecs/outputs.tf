output "demo_url" { value = "http://${aws_lb.app.dns_name}" }
output "ecr_repository_url" { value = aws_ecr_repository.app.repository_url }
