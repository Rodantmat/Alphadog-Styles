package montink

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/brunoapolinariodev/montink_erp/internal/domain"
)

type Client struct {
	token      string
	baseURL    string
	httpClient *http.Client
}

func NewClient(token string) *Client {
	return &Client{
		token:   token,
		baseURL: "https://api.montink.com",
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (c *Client) GetOrders() ([]domain.Order, error) {
	var fullURL = fmt.Sprintf("%s/orders", c.baseURL)
	req, err := http.NewRequest("GET", fullURL, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Add("Authorizationtoken", c.token)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("Error on request: %s", resp.Status)
	}

	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {

		}
	}(resp.Body)

	var response domain.MontinkOrderResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	if !response.Success {
		return nil, fmt.Errorf("api error: %s", response.Message)
	}

	return response.Orders, nil

}

// GetOrder fetches specific details of a single order by its ID.
// Returns an OrderDetail struct containing nested customer and product data.
func (c *Client) GetOrder(id string) (*domain.OrderDetail, error) {
	fullURL := fmt.Sprintf("%s/order/%s", c.baseURL, id)

	req, err := http.NewRequest("GET", fullURL, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorizationtoken", c.token)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to get order: status %s", resp.Status)
	}

	var response domain.OrderDetail
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	// Sometimes the API returns 200 OK but with success: false in the body
	if !response.Success {
		return nil, fmt.Errorf("api error: %s", response.Message)
	}

	return &response, nil
}
